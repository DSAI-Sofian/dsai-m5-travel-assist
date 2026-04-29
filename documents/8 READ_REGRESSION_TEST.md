# REGRESSION TEST

- [REGRESSION TEST](#regression-test)
  - [Codex Prompt:](#codex-prompt)
  - [Follow-up Regression Test Report](#follow-up-regression-test-report)
    - [Test Environment](#test-environment)
    - [Summary Table](#summary-table)
    - [Detailed Findings](#detailed-findings)
    - [Final Recommendation](#final-recommendation)
  - [TEST RESULTS](#test-results)
  - [Follow-up Regression Test Report](#follow-up-regression-test-report-1)
    - [Test Environment](#test-environment-1)
    - [Summary Table](#summary-table-1)
    - [Detailed Findings](#detailed-findings-1)
    - [Final Recommendation](#final-recommendation-1)


## Codex Prompt:
Please help me test the Telegram follow-up behaviour for the Travel Assist bot.

Context:
The bot supports follow-up messages after a successful itinerary has already been generated. The follow-up options shown to users are:

- cheaper option
- more comfort please
- add more food places
- make it less rushed
- add nature activities
- add more activities

Task:
1. Inspect the code paths related to follow-up handling, especially telegram_bot.py.
2. Confirm how chat_last_payloads, is_followup_request(), and apply_followup_preferences() work.
3. Check whether each follow-up option is detected correctly.
4. Check whether each option modifies the payload appropriately.
5. Check whether "add more activities" is intentionally handled without mutating preferences.
6. Run or create lightweight tests if practical.
7. Produce a report with this structure:

## Follow-up Regression Test Report

### Test Environment
- Files inspected:
- Commands run:
- Any limitations:

### Summary Table
| Follow-up message | Detected as follow-up? | Payload changed? | Expected behaviour | Pass/Fail | Notes |
| ----------------- | ---------------------: | ---------------: | ------------------ | --------- | ----- |

### Detailed Findings
For each follow-up option, explain:
- whether it is detected
- what preferences are added, if any
- whether feedback is passed to backend
- any risk or bug

### Final Recommendation
State whether this is safe for presentation tomorrow.

Important:
Do not refactor the bot unless a serious bug is found.
Prefer inspection and lightweight tests.
If code changes are needed, propose them first before editing.

---

## TEST RESULTS

## Follow-up Regression Test Report

### Test Environment
- Files inspected:
- [telegram_bot.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/telegram_bot.py#L22)
- [conversation_interpreter.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/intelligence/conversation_interpreter.py#L7)
- [feedback_interpreter.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/intelligence/feedback_interpreter.py#L6)
- [workflow.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/orchestrator/workflow.py#L192)
- [abuse_guard.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/security/abuse_guard.py#L323)
- Commands run:
- `rg -n "chat_last_payloads|is_followup_request|apply_followup_preferences|..."`
- `nl -ba app/telegram_bot.py | sed -n '1,700p'`
- `nl -ba app/intelligence/conversation_interpreter.py | sed -n '1,260p'`
- `nl -ba app/intelligence/feedback_interpreter.py | sed -n '1,260p'`
- `nl -ba app/orchestrator/workflow.py | sed -n '220,520p'`
- AST-based lightweight Python checks of `is_followup_request()` and `apply_followup_preferences()`
- Any limitations:
- End-to-end Telegram test was not run because `python-telegram-bot` is missing in this environment (`ModuleNotFoundError`), so checks were function-level and code-path inspection.

### Summary Table
| Follow-up message     | Detected as follow-up? | Payload changed? | Expected behaviour                                                | Pass/Fail | Notes                                                                          |
| --------------------- | ---------------------: | ---------------: | ----------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------ |
| cheaper option        |                    Yes |              Yes | Should bias toward budget                                         | Pass      | Adds budget preferences; feedback also drives `Budget Saver` variant selection |
| more comfort please   |                    Yes |              Yes | Should increase comfort                                           | Pass      | Adds comfort preferences; backend continuity also applies comfort adjustments  |
| add more food places  |                    Yes |              Yes | Should add food emphasis                                          | Pass      | Adds food preferences; continuity adds restaurant stops                        |
| make it less rushed   |                    Yes |              Yes | Should relax itinerary pace                                       | Pass      | Adds relaxed-pace preferences; continuity applies slower pacing                |
| add nature activities |                    Yes |              Yes | Should increase nature content                                    | Pass      | Adds nature preferences; continuity adds nature attractions                    |
| add more activities   |                    Yes |               No | Should be handled by feedback/continuity, not preference mutation | Pass      | Intentionally no preference mutation; continuity handles activity expansion    |

### Detailed Findings
- cheaper option
- Detection: `is_followup_request()` matches `"cheaper"` ([telegram_bot.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/telegram_bot.py#L68)).
- Preferences added: `budget`, `cost saving`, `affordable` ([telegram_bot.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/telegram_bot.py#L149)).
- Feedback passed: yes, via `payload["feedback"] = text` in follow-up branch ([telegram_bot.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/telegram_bot.py#L571)).
- Risk: continuity interpreter does not tag cheaper as `has_followup`; cheaper handling depends on feedback interpreter/variant selection path.

- more comfort please
- Detection: yes (`"more comfort"` phrase).
- Preferences added: `comfort`, `luxury`, `better hotel`, `relaxed stay`.
- Feedback passed: yes.
- Risk: none critical; both Telegram preference mutation and backend continuity support it.

- add more food places
- Detection: yes.
- Preferences added: `food`, `restaurants`, `local cuisine`, `street food`.
- Feedback passed: yes.
- Risk: none critical; continuity also appends extra restaurant suggestions.

- make it less rushed
- Detection: yes.
- Preferences added: `relaxed pace`, `less rushed`, `fewer activities per day`.
- Feedback passed: yes.
- Risk: none critical; continuity sets pace to relaxed and adds buffer text.

- add nature activities
- Detection: yes.
- Preferences added: `nature`, `outdoor`, `parks`, `scenic viewpoints`, `natural attractions`.
- Feedback passed: yes.
- Risk: none critical; continuity adds nature attractions and activity budget delta.

- add more activities
- Detection: yes.
- Preferences added: none by design (`pass` block; explicit comment says continuity should handle it) ([telegram_bot.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/telegram_bot.py#L143)).
- Feedback passed: yes.
- Risk: low; behavior is intentional and backend continuity adds activities/attractions.

Additional note on `chat_last_payloads`:
- It stores last successful request per `chat_id` ([telegram_bot.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/telegram_bot.py#L22), [telegram_bot.py](/home/s_sofian/dsai/module_05/dsai-ft2-capstone-travel-assist/app/telegram_bot.py#L597)).
- Follow-up requires both `is_followup_request(text)` and existing `chat_last_payloads[chat_id]`.
- Minor risk: `apply_followup_preferences()` mutates the `preferences` list object (shallow-copy behavior), so state can change even before backend success.

### Final Recommendation
Safe for presentation tomorrow, with one caveat to keep in mind: follow-up behavior for the six listed commands is working as expected in code and lightweight tests, but full Telegram end-to-end verification was not executed in this environment due missing `python-telegram-bot`.