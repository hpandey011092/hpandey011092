# CLAUDE.md — ISKCON / HKM donation-calling account (Blue Machines)

Context file for any Claude session working on ISKCON with Himanshu. Built 18 Nov 2026 from Slack (#iskcon_internal_com, #bm-telephony-alerts, group DM with ayushman/Harshdeep/Swathi), Granola (17 & 18 Nov ISKCON meetings, RevOps 22 Oct, Delivery check-ins 31 Aug / 15 Sep / 2 Nov / 9 Nov, Chola internal 26 Oct) and Drive (Tanmay's Diwali Planning doc + decks, Ishaan's Cohort_Analysis_v7).
**Not covered:** WhatsApp (no connector in this session). Docs Tanmay sent on WhatsApp that are NOT in Drive, such as the "Diwali procedure" doc and the Janmashtami completion report, are missing from this file.

Your role in this account: you are Himanshu's project planner and verifier, not the builder. Swathi builds the agents, Ishaan and Jagan run the workflows, and ayushman owns the client. Himanshu's job is to catch misses before the campaign goes live.

---

## 1. Account in one paragraph
ISKCON / Hare Krishna Movement (HKM, Hyderabad entity) runs festival donation campaigns. BM runs outbound AI calls. Commitments get a payment link (WhatsApp via Karix → RCS → SMS, plus a personal-number WhatsApp via WbizTool), and a follow-up agent calls people who committed but did not pay. Payments come back from HKM's Razorpay payload. Success is measured as **ROAS = donations ÷ BM spend** (spend = call billing + Karix messaging). Target ≥1.5×. BM revenue by month: Sep ₹14.6L → Oct ₹3.4L → Nov ₹2.1L, and the account is flagged as a GRR risk. Each campaign has to land cleanly to keep budgets flowing (New Year campaign: ₹7L).

## 2. Campaign history (numbers to quote)
| Campaign | Dates | Scale | Outcome | Lesson |
|---|---|---|---|---|
| Janmashtami | 24 Aug–4 Sep | ~7.7L devotees attempted, 2.95L connected (19.6%) | 153 payers. Deck: ₹7.88L donations, ROAS warm/hot 1.70× and cold 0.20×. BM revenue ~₹15L | Male "Gopal" voice gave 3× the commitments. "ISKCON Hyderabad" worked better as the caller name. Cold leads lose money. WhatsApp was blocked mid-campaign |
| Pitru Paksha | 6/8–10 Oct | ~6.5L calls | ~129 payers, ROAS ~0.5. ₹25L committed on calls, only ₹1.5–2L converted | Half the payment links never arrived: Karix had no status webhook, no SMS/RCS, and the IP was not whitelisted. Hot/warm/cold shared one workflow and got mixed up |
| Diwali | 2–8 Nov | 1,00,228 people, 2,20,190 calls | 2,833 commitments, 212 paid, ₹3.25L collected vs ₹2.07L cost = **1.57×**. Hot 9.98×, warm 2.93×, cold 0.42×, follow-up 8.63× (13× quoted on 18 Nov) | Launch day failed on 429s because CPS had been returned to the pool with no heads-up. Seva list changed at the last minute. "ISKCON" was spelled letter by letter in ~2,000 calls |
| **Kartik Purnima** | **22–24 Nov** | ₹2L budget | — | See `KARTIK_PURNIMA_PLAN.md` |
| Vaikuntha Ekadashi | ~17–19 Dec (unconfirmed) | — | — | — |
| New Year | from 26 Dec | ₹7L budget, ~10L calls | target ≥1.5×, ₹25L donations | Needs infra provisioning and the number-rotation fix |

Known contradictions in the numbers (do not quote without checking):
- Follow-up ROAS: 13× (18 Nov) vs 8.63× (9 Nov).
- Diwali answer rate: "32%" vs about 20% at call level.
- Janmashtami: ₹7.88L vs 153 payers with a ₹5,008 maximum payment.

## 3. System architecture (Calling Workflow HTML, Aayush 28 Oct; Pitru Paksha HTML, Jagan 7 Oct)
1. **CSV lead push** into the console Campaign Manager. The console is the CRM; there is no CRM and no Nautilus yet. CSV only, max 5 MB.
   Schema: `externalUserId, externalWorkId, firstName, lastName, phoneNumber, email, lead_id, preferred_language, seva_name, donation, lead_segment`.
   `externalWorkId` must be **unique per festival**, or the call is silently skipped.
   Upload ramp: 1 → 20 → 200 → rest. **Never upload to the follow-up workflow.**
2. Calling strategy (image).
3. Trigger workflow:
   - 3A: number whitelisting.
   - 3B: rotation when a number is marked as spam.
   - Ishaan maps both by hand. Numbers are weighted (33 on primary numbers, 1 on backups). **Deleting a number mid-run breaks the retry logic.**
   - Pre-dial checks: business hours, festival window, already paid (HKHT link or website), and fail-closed if a check can't be read.
4. **AI calling agent.** Four separate workflows: Hot / Warm / Cold / Follow-up.
   - Calling windows 8–11 AM and 5/7–9 PM. 3 retries per lead per day (retry every 3 h).
   - **180 s hard stop** with an abrupt cut.
   - Mid-call tools: `send_donation_link`, `check_link_delivery`.
5. High intent → **WhatsApp link via Karix** (utility template, ~80% delivered).
6. 6A: Karix webhook returns WhatsApp status. 6B: if it fails, WbizTool personal-number WhatsApp within 5 min.
   - RCS → SMS fallback (RCS ~32% delivered, SMS ₹0.12/msg).
   - WbizTool is capped at 100–150 messages per number, has 1 number wired, and brought ₹23K in Diwali.
7. Live dashboard (Jagan, run.app): payments arrive in about 10 s through Razorpay. The data source (MongoDB vs unified table) is **unknown**.
8. Paid? If not paid after 24 h (the HTML says 4 h; the 24 h practice is what runs) → follow-up agent → same route from stage 5.
9. Dedupe / DND list manager.

**Pending items still open on 18 Nov:**
- P1: WhatsApp-status webhook (Karix rule 37484 never activated).
- P2: BM IP whitelisting.
- P3: Ownership of stages 5–7.
- P4: RCS/SMS fallback.
- P5: Seva and benefits content.

## 4. Lead data
- **ISKCON base:** ~8L. Hot + warm 1.2L, cold 5.8L.
  - Hot = committed but never paid.
  - Warm = donated at least once.
  - Cold = never donated, low ROAS.
- **Vendor base:** ~5L. **Excluded for Kartik.**
- **Ishaan's Cohort_Analysis_v7:**
  - Covers Janmashtami and Pitru Paksha only. **It has no Diwali cohort, yet Diwali committed-but-unpaid is the preferred Kartik cohort.**
  - Holdouts:
    - random amounts (>₹25K or <₹100): 159
    - non-genuine engagement: 214
    - voicemail/IVR: 2,890 (retry these)
    - "claims already paid" but not in the donor list: 2,712 (the temple should verify these; they are not leads)
  - ~19K rows have NO NAME ON RECORD.
- Access is restricted. Do not copy lead PII into docs, Slack or this repo.
- **The "hot/warm" names are not consistent.** Tanmay's doc calls committed-but-unpaid "Warm"; the 18 Nov meeting calls it "Hot". Always state the definition.

## 5. Pronunciation and TTS rules (hard rules for any prompt or variable that reaches TTS)
Root cause pattern: Cartesia/Sonic reads ALL-CAPS tokens letter by letter, and English-locale TTS anglicises Sanskrit words.
| Term | Failure seen | Rule |
|---|---|---|
| ISKCON | spelled "I-S-K-C-O-N" in ~2,000 Diwali calls | Generate as **इस्कॉन** (Devanagari) or lowercase "iskcon". Never all caps in LLM output, the first message or variables |
| Hare Krishna | "Hair Krishna" (PP 8–9 Oct), "HAARE Krishna" (Diwali 1 Nov); the "Arrey कृष्णा" patch did not hold | Write **हरे कृष्ण** in Devanagari everywhere, including the English agent |
| SEVA, other caps words | "S-E-V-A" letter by letter (Janmashtami 31 Aug) | Lowercase or Devanagari (सेवा). Ban all caps in prompts and seva-name variables |
| Seva slugs | follow-up bot could read "annadana-seva-diwali" aloud | Pass a display name (अन्नदान सेवा / गौ सेवा), never a slug |
| Names with initials | "एन वी एस जे" spoken letter by letter | Normaliser drops initials. Fallback to "devotee", **never "anonymous"** |
| Amounts | spoken in the wrong language (Telugu/Hindi) in the first turn | Pass the amount as words in the call language, or speak it from turn 2 |
| Bal Gopal | said "balTulsi" | Check seva and deity names per language |
| Any term | pronunciation library is skipped when detected language = "unknown"; console pronunciation column showed 0 words (Oct, cross-account) | Do not rely only on the console dictionary. Fix the spelling at the source (prompt/LLM output) |

Test every language the campaign dials (Hindi, English, Telugu, Kannada, Marathi, Tamil) with all of the above. Check TTS model parity across main and follow-up agents: Janmashtami's follow-up ran a different Sonic version.

## 6. Owner map (who to talk to)
| Problem | Person |
|---|---|
| Client, approvals, budget, seva list, lead cohort choice, client WhatsApp reports | **ayushman** (client side: Mukunda Prabhu approves amounts and bots; Balaganesh owns Karix at HKM; Mahabhuja Prabhu holds the Karix OTP) |
| Covering Aayush's role on ISKCON now; provisioning heads-up; dashboard source; testers | **Harshdeep** (not long-term on ISKCON) |
| Agent and bot build, prompt, end-call, good/bad call sheet, testing PM | **Swathi** |
| Workflow ops: upload, dedup/normalisation, number mapping and rotation, pause/terminate, eval edits, cohorts | **Ishaan** (part-time, spread across projects) |
| Built the workflow and Karix/HKM/Wbiz integrations; dashboard; SMS vs WhatsApp channel strategy; Karix cost | **Jagan** (the one person the dashboard depends on) |
| CPS, concurrency, Vobiz provisioning; watches #bm-telephony-alerts; **heads-up before every launch** | **Vivek** (Prashant's team) |
| Escalation for infra, stack choice (LLM/TTS/STT), language testers | **Chetan Agarwal** |
| Infra | **Prashant Bhargava**, **Chetan Rao** |
| Vobiz account and billing (open ₹3.45L auto-renewal dispute) | **Akshay Kumar** |
| Language switching, pronunciation config, LLM fallbacks | **Gokulram**; platform voice bugs: **Sandeep** |
| Testers | Bhavana (Marathi), Rupesh Sen (Hindi), Chenna Keshav (Telugu), Nidhishree (Kannada), Gokulram (Tamil), Neil (Gujarati) |
| Exec sponsor; number-rotation design input | **Tanmay** |
| Manager, copy on provisioning; CRM idea | **Abhishek Ranjan** |

## 7. Standing lessons (things that broke before and will break again)
1. **No CPS heads-up → launch-day 429s** (Diwali 2 Nov). Vivek needs volume and timing before every launch.
2. **Number rotation and retry live inside the workflow.** Removing a number breaks retries. Tanmay's fix is still undone (deferred to Dec/New Year). Never delete a number mid-run; change weights instead, and expect a terminate/restart.
3. **Business-hours defaults (19:00 cutoff) revert** per number. Re-check them before every trigger.
4. **No queue flush.** Calls kept going after 7:30 PM in Janmashtami. Know the stop procedure (business hours → delink numbers) before you need it.
5. **Seva changes late** break bots, eval, `hot_wa_send` hard-coding and links. HKM's site caches link redirects (still open).
6. **Karix fallback is not trustworthy.** No delivered status, so SMS never triggers. "It worked in Diwali" means WhatsApp worked, not the fallback chain.
7. **Config drift between agents:** LLM, TTS version, AMD off, reasoning effort low, Marathi stack wrong, a call-length cap missing.
8. **Duplicates re-called** in Pitru Paksha. Dedup before upload, not during.
9. **"It went well" ≠ "it is fixed."** Diwali's 1.57× hid the open rotation, Karix and Wbiz items. Check status from evidence, not sentiment.
10. Secrets (dashboard password, ISKCON API key) are posted in plain text in #iskcon_internal_com. Ask for rotation; never copy them.

## 8. Working agreements
- Himanshu's golden rule for Kartik: **no new experiments**. Save them for the Dec and New Year campaigns.
- Client report: morning and evening, three lines (Donation / Spend / ROAS). Spend includes Karix cost.
- Stop-loss: ₹50K spent without ROAS → stop. Agree in advance that a stop is not an "agent was bad" escalation.
- When status is unknown, write `[confirm]`. Never mark something done without a message, recording or screenshot as evidence.
