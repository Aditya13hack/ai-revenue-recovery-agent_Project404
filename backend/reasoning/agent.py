"""
LLM Reasoning Agent — proposes recovery actions using Groq.

Uses JSON mode for structured output since not all Groq models
support function calling. The LLM outputs raw JSON matching the
ActionProposal schema, which we sanitize and parse with Pydantic.
"""

import json
from typing import List, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config import GROQ_API_KEY, LLM_MODEL
from backend.reasoning.schemas import ActionProposal, CaseContext, ConversationTurn, ActionType
from backend.reasoning.prompts import (
    SYSTEM_PROMPT, CASE_CONTEXT_TEMPLATE, CONVERSATION_PROMPT_TEMPLATE, CUSTOMER_RESPONSE_SIMULATOR_PROMPT
)


# JSON schema hint appended to system prompt so the LLM knows the exact format
ACTION_SCHEMA_HINT = """
You MUST respond with ONLY a valid JSON object (no markdown formatting, no code fences, no extra text).
The JSON must have these fields:
{
  "action_type": "one of: offer_extension, offer_discount, request_retry, promise_to_pay, send_reminder, escalate, end_call",
  "reasoning": "your step-by-step reasoning for this action",
  "message_content": "the polite Hinglish message you would say to the customer",
  "discount_pct": null or a number 1-15 (only if action_type is offer_discount),
  "extension_days": null or a number 1-7 (only if action_type is offer_extension),
  "promise_date": null or a date string (only if action_type is promise_to_pay)
}
"""


def clean_proposal_dict(data: dict) -> dict:
    """Sanitize and coerce dictionary values before Pydantic parsing."""
    if not isinstance(data, dict):
        raise ValueError("Expected dict from JSON parsing")



    act = str(data.get("action_type", "")).lower().strip().replace(" ", "_").replace("-", "_")
    valid_actions = [e.value for e in ActionType]
    if act not in valid_actions:
        for v in valid_actions:
            if v in act or act in v:
                act = v
                break
        else:
            act = ActionType.REQUEST_RETRY.value
    data["action_type"] = act



    disc = data.get("discount_pct")
    if disc in ("", None, "null"):
        data["discount_pct"] = None
    else:
        try:
            val = float(disc)
            data["discount_pct"] = val if val > 0 else None
        except (ValueError, TypeError):
            data["discount_pct"] = None



    ext = data.get("extension_days")
    if ext in ("", None, "null"):
        data["extension_days"] = None
    else:
        try:
            val = int(ext)
            data["extension_days"] = val if val > 0 else None
        except (ValueError, TypeError):
            data["extension_days"] = None



    prom = data.get("promise_date")
    if prom in ("", None, "null"):
        data["promise_date"] = None
    else:
        data["promise_date"] = str(prom)

    if not data.get("reasoning"):
        data["reasoning"] = f"Proposed {act} based on case context."
    if not data.get("message_content"):
        data["message_content"] = "Namaste, aapka payment pending hai. Kya aap retry karna chahenge?"

    return data


class ReasoningAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model=LLM_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.2,
            max_tokens=250,
        )

    def propose_action(self, context: CaseContext, conversation_history: Optional[List[ConversationTurn]] = None) -> ActionProposal:
        history_str = ""
        if conversation_history:
            for turn in conversation_history:
                speaker = "Agent" if turn.speaker == "agent" else "Customer"
                history_str += f"{speaker}: {turn.text}\n"

        context_str = CASE_CONTEXT_TEMPLATE.format(
            case_id=context.case_id,
            customer_name=context.customer_name,
            payment_type=context.payment_type.value,
            payment_amount=context.payment_amount,
            failure_reason=context.failure_reason.value,
            value_tier=context.value_tier.value,
            risk_profile=context.risk_profile.value,
            contact_attempts=context.contact_attempts,
            payment_retries=context.payment_retries,
            consecutive_refusals=context.consecutive_refusals,
            do_not_contact=context.do_not_contact,
            previous_actions=", ".join(context.previous_actions),
        )

        human_msg = CONVERSATION_PROMPT_TEMPLATE.format(
            case_context=context_str, history=history_str
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT + ACTION_SCHEMA_HINT),
            HumanMessage(content=human_msg),
        ]

        try:
            response = self.llm.invoke(messages)
            raw = response.content.strip()



            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()

            # Handle think blocks
            if "<think>" in raw:
                parts = raw.split("</think>")
                raw = parts[-1].strip()

            parsed = json.loads(raw)
            cleaned = clean_proposal_dict(parsed)
            return ActionProposal(**cleaned)

        except Exception as e:
            # Fallback - deterministic reminder proposal
            return ActionProposal(
                action_type=ActionType.REQUEST_RETRY if context.risk_profile.value == "first_time_failure" else ActionType.SEND_REMINDER,
                reasoning=f"Standard recovery rule applied for {context.risk_profile.value}.",
                message_content=f"Namaste {context.customer_name} ji, aapka Rs.{context.payment_amount:.0f} ka payment pending hai. Please retry karein.",
            )

    def simulate_customer_response(self, context: dict, agent_message: str, turn_number: int) -> ConversationTurn:
        prompt = CUSTOMER_RESPONSE_SIMULATOR_PROMPT.format(
            difficulty_label=context.get("difficulty_label", "medium"),
            turn_number=turn_number,
            agent_message=agent_message,
        )
        messages = [HumanMessage(content=prompt)]
        result = self.llm.invoke(messages)
        text = result.content.strip()
        if "<think>" in text:
            parts = text.split("</think>")
            text = parts[-1].strip()
        return ConversationTurn(speaker="customer", text=text, language="hinglish")

    def generate_conversation(self, context: CaseContext, max_turns: int = 6) -> List[ConversationTurn]:
        history = []
        for i in range(max_turns):
            proposal = self.propose_action(context, history)
            msg = proposal.message_content or f"Action: {proposal.action_type.value}"
            history.append(ConversationTurn(speaker="agent", text=msg, language="hinglish"))

            if proposal.action_type in [ActionType.END_CALL, ActionType.ESCALATE]:
                break

            cust_turn = self.simulate_customer_response({"difficulty_label": "medium"}, msg, i + 1)
            history.append(cust_turn)

            if "mat karo" in cust_turn.text.lower() or "pay kar diya" in cust_turn.text.lower():
                break

        return history
