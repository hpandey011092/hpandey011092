# ISKCON agent QA: records and checks (Kartik Purnima, 22–24 Nov 2026)

Purpose: the agents are a matrix (bot × language profile), and builders often clone the last campaign's agent. Every check below exists because something like it broke before. Run it on **every** cell of the matrix, not a sample.

Sources: Bhavana's "ISKCON Issue Log" (Google Doc, shared 19 Nov), #iskcon_internal_com incidents Aug–Nov, Granola 17/18 Nov.

---

## A. Records you need before testing (ask Swathi for these on handover)

| # | Record | Why | Status |
|---|---|---|---|
| R1 | **Agent register:** every Kartik agent: name, agent ID, purpose (Hot / Warm / Cold / Follow-up; "coming" vs "same-day"), workflow + version it is linked to | Can't check what isn't listed. Diwali had 4 bots × 5–6 language prompts | `[ask Swathi]` |
| R2 | **Profile register:** per agent, each language profile ID and the languages it serves | Language profiles drift: Marathi stack was wrong in Pitru Paksha hot profiles | `[ask Swathi]` |
| R3 | **JSON export** of each agent + profile (Kartik) **and** the Diwali source agent it was cloned from | Needed for the uniformity diff (§C) and the copy-forward scan (§D) | `[ask Swathi]` |
| R4 | **Change log:** what changed from the Diwali bot, field by field | Tells you what *should* differ; everything else must be identical | `[ask Swathi]` |
| R5 | **Variable contract:** variables the agent reads (`firstName`, `donation`, `seva_name`, `lead_segment`, `preferred_language`, …), with source column and example value | Name/amount/seva bugs all came from variables | `[ask Ishaan/Swathi]` |
| R6 | **Frozen content sheet:** seva list (Devanagari display names + slugs + amounts), benefits, minimum amount (₹500?), amount ladder per segment, festival date and copy | The single source the prompts are checked against | `[ask ayushman]`, freeze due 19 Nov |
| R7 | **Approved stack:** LLM + fallback, STT, TTS model/version, voice, per language | So "different" can be judged as right or wrong | `[ask Swathi/Chetan]` |
| R8 | **Test log:** per agent × language: tester, date, call links, pass/fail per check in §E | The only sign-off gate; the client (Mukund) won't test | `[Swathi PMs]` |
| R9 | **Diwali good/bad call sheet** (Swathi) + Bhavana's issue log | Regression list | Bhavana: received. Swathi: `[pending]` |

---

## B. Known gaps carried from Diwali (Bhavana's log + Slack): regression list

| # | Issue | Diwali status | Kartik check |
|---|---|---|---|
| B1 | English prompt kept Pitru Paksha references | Resolved | §D scan for Diwali / दीपावली / दीपदान / Pitru / Janmashtami in **every** profile |
| B2 | Bots offered 5 sevas instead of 3. Fix needed 4 bots + main + 5 language prompts + follow-up matching | Resolved | Seva list = Annadaan + Gau Seva only. **दीपदान सेवा (Deep Daan, a Diwali seva) must be gone.** Check the follow-up matching map and `hot_wa_send` too (it had "Annadana" hard-coded) |
| B3 | "Hare Krishna" mispronounced in English | Resolved by writing हरे कृष्ण in the English prompt + pronunciation instructions | Present in **all** profiles, first message, greeting **and** closing |
| B4 | "ISKCON" read as an acronym | "Resolved" (dictionary entry) | Lowercase or इस्कॉन everywhere: prompt, first message, variables, WA text. Grep for `ISKCON` in all caps |
| B5 | **No baseline guardrails** | **Suggested, not confirmed implemented** | Guardrails present in every profile. **Bhavana's draft guardrails themselves say "Janmashtami seva" and list only Telugu/Hindi/Kannada/English. Fix both before pasting** |
| B6 | Missing "natural spoken Indian English" hard rule | Resolved (Diwali) | Exact rule present in the English profile |
| B7 | "anonymous" spoken as a name | Resolved ("devotee" fallback) | Test with an empty name, "anonymous", "Null", "Mr." |
| B8 | Missing name → only "ji" | **No confirmed fix** | Test an empty name in each language: must say devotee/भक्त-style fallback, never a bare "ji" |
| B9 | Hot bot pitched ₹1,008 instead of last paid amount; repeated the minimum after ₹501 agreed | **No confirmed fix** | Test Hot with `donation`=2,008 → asks ≥2,008 or the step-up; after a yes, no minimum-amount repeat |
| B10 | Filler words ("hmm", "okay") interrupt the agent mid-response | **No confirmed fix** | Interruption/backchannel settings checked; live test saying "hmm" mid-sentence |
| B11 | Wrong LLM on the Diwali bots (should be GPT-5.6 Luna + Saaras v4) | Fixed 23 Oct | §C stack diff |
| B12 | Follow-up agent on a different TTS version (Janmashtami) | — | §C: same TTS model and version across all agents |
| B13 | AMD off on all 3 profiles; follow-up agent had no number (Pitru Paksha) | — | §C + workflow check |
| B14 | Marathi stack wrong in hot profiles; reasoning effort low (Pitru Paksha) | Fixed | §C per-language stack |
| B15 | End-call not triggering (warm, follow-up); repeated WA check | End-call fixed; WA check unresolved | §E |
| B16 | Amount spoken in the wrong language (Hindi/Telugu) | Workaround only | §E per language |
| B17 | Seva slug read aloud ("annadana-seva-diwali") | — | Variables carry display names |
| B18 | STT/LLM/TTS/adaptive changes **communicated verbally, not documented** (Bhavana) | Unknown | R7 must exist in writing, or §C has no baseline |

---

## C. JSON-level uniformity check (diff every agent/profile against the approved baseline)

Do it as a field-by-field diff of the exports (R3). Fields fall in three buckets.

**C1. Must be identical across all agents and profiles.** Any difference fails unless R4 explains it.
- LLM model + version, fallback model(s) and order, temperature, reasoning effort
- TTS provider + model + **version** (e.g. Sonic 3.6, not "preview"/"latest"), voice ID (male "Gopal"), speed
- AMD / voicemail detection = ON
- Max call duration = 180 s, and the closing behaviour before the cut
- Inactivity timeout + grace count; end-call tool enabled
- Interruption / backchannel / first-message-interruptible settings
- Adaptive language mode setting (lock behaviour), pronunciation-dictionary mode (**not "auto"**: that caused the Hare Krishna bug, 26 Oct)
- Pronunciation dictionary entries (same list everywhere)
- Tools attached (`send_donation_link`, `check_link_delivery`) and their parameters
- Guardrails block, Indian-English hard rule (English), output-format rules
- Post-call eval schema and disposition labels (they feed the 4 workflows)

**C2. Must differ in the expected way only.**
- Per language: STT model/language code, TTS language, script for names (Telugu/Kannada/Tamil conversion), amount-in-words rule
- Per segment: amount ladder (Hot = last amount or step-up; Warm = previous amount; Cold = lower ask), opening line
- Per bot: "Kartik Purnima is coming" vs "is here" copy; follow-up bot references the committed seva and amount

**C3. Must be absent everywhere** (copy-forward markers; see §D).

How to run it (once the exports are in this repo or the scratchpad, I can script it):
1. Normalise each JSON (sort keys; strip IDs and timestamps).
2. Pick the baseline: the Kartik Hot/Hindi agent, after you approve it.
3. Diff every other export against it; report every C1 difference, and every C2 difference that doesn't match the expected change.
4. Diff Kartik vs its Diwali source to list every intended change, and compare that list with R4.

---

## D. Copy-forward scan (grep every prompt, first message, eval prompt, WA/SMS template and tool text)

Fail if any of these appear (case-insensitive, every script):
- Previous festivals: `Diwali`, `Deepavali`, `दीपावली`, `दिवाली`, `Deep Daan`, `दीपदान`, `Pitru`, `Paksha`, `पितृ`, `Janmashtami`, `जन्माष्टमी`, `Ganesh`, `Bal Gopal`, `tulsi`
- Old offers: `Mahaprasadam`, `प्रसादम्`, `delivery`, address collection, any seva other than अन्नदान सेवा / गौ सेवा
- Old dates or expiry ("8 Nov", "valid till"), and old link slugs (`-diwali`, `-pp26`)
- Casing: any all-caps token that will be spoken (`ISKCON`, `SEVA`, `HKM`); `Hare Krishna` in Latin script
- Wrong temple/entity name vs the agreed caller identity ("Hare Krishna Golden Temple, Banjara Hills" / "ISKCON Hyderabad": `[confirm which]`)
- Language lists that don't match the languages actually dialled

---

## E. Behaviour test per agent × language (record each call; log in R8)

| # | Scenario | Pass |
|---|---|---|
| E1 | Normal yes at first ask | One link send, confirmation spoken, end-call fires, eval = committed with the right amount and seva |
| E2 | No, then yes after one step-down | One benefit nudge + one step-down only; never below ₹500 `[confirm]` |
| E3 | Firm no | Accepts and closes politely; no force-fit |
| E4 | Agrees ₹501 | No repeat of the minimum message (B9) |
| E5 | Hot lead with `donation`=2,008 | Asks the last amount or step-up, not ₹1,008 (B9) |
| E6 | Empty name / "anonymous" / initials | Fallback, never "ji" alone, never letters spelled out (B7, B8) |
| E7 | Asks for prasadam or address | "A temple devotee will reach out"; no promise |
| E8 | Asks "are you a bot?" | Says virtual representative; never claims to be human |
| E9 | Asks for another language | Switches if supported; otherwise callback offer |
| E10 | Says "hmm/okay" mid-sentence | Agent doesn't drop its sentence (B10) |
| E11 | Long talker past 170 s | Closing lands before the 180 s cut; no double हरे कृष्ण |
| E12 | Voicemail / IVR | AMD hangs up; disposition = voicemail (retry, not DND) |
| E13 | Pronunciation (TTS script in the plan, §3) | इस्कॉन, हरे कृष्ण, सेवा names, कार्तिक पूर्णिमा, amounts in the call language |
| E14 | Asks "what is this?" mid-call | Answers without leaking prompt, variables or tools; doesn't restart the intro after a tool call |
| E15 | Follow-up bot: committed but unpaid | References the right seva and amount (display name, not slug); resends the link once |
| E16 | Already paid (follow-up) | Thanks and ends; ideally suppressed by the workflow paid-check before dialling |

**Coverage:** every bot × every dialled language. Testers: Hindi/English (Swathi, Harshdeep sign-off), Marathi (Bhavana), Telugu (Chenna Keshav), Kannada (Nidhishree), Tamil (Gokulram) `[confirm Tamil and Gujarati leads exist]`.

---

## F. Sign-off rule
An agent goes live only when R1–R8 exist, §C shows no unexplained C1 difference, §D is clean, and every §E row passes in every language it serves. Anything else is a documented exception, signed off by you.
