# Kartik Purnima (22–24 Nov 2026): Himanshu's pre-flight plan and miss-catcher

Read with `CLAUDE.md` (same folder). Status as of **Wed 18 Nov, evening**. `[confirm]` = no evidence either way.
Budget ₹2L · stop-loss ₹50K without ROAS · target ≥1.5× · no new experiments.

---

## 0. The ten things most likely to bite (ranked)
| # | Risk | Why I think it's live | Owner to chase | What "closed" looks like |
|---|---|---|---|---|
| 1 | **No CPS/concurrency heads-up → 429s at 8 AM on the 22nd** | Diwali 2 Nov: almost all of the first 2K-lead batch failed with 429s, and it happened **twice** that morning. ISKCON capacity goes back to the pool between campaigns, and Ishaan set 5 CPS per number while only ~1 was available. Re-triggering failed calls had to go through groundcover because there is no status filter. **Shared CPS is only available to ISKCON before 10 AM or after 7 PM (cap 43)**, so the 10–11 AM part of the morning slot competes with other customers | Harshdeep sends to **Chetan + Prashant, cc Vivek + Abhishek Ranjan**; **Vivek** acknowledges | Vivek confirms in writing the CPS/concurrency for 22–24 Nov against a volume number (leads × 3 retries), **including 10–11 AM**, or the morning push ends at 10. Per-number CPS in the workflow matches what is allocated |
| 2 | **Pronunciation: ISKCON / Hare Krishna / seva names** | "Hair/HAARE Krishna" was open from 8 Oct to 1 Nov with no confirmed fix. ISKCON caps fixed only via the console dictionary, which is skipped when language = unknown | **Swathi** (build), Gokulram (config) | Prompt, first message, eval and WA templates use इस्कॉन / हरे कृष्ण / सेवा (Devanagari) or lowercase. Recorded test call per language passes the TTS checklist in §3 |
| 3 | **Number rotation and retry inside the workflow** | Tanmay's fix is not built. On 18 Nov you made it Ishaan's "main task", at least to find out why it wasn't done; its scope for Kartik is unclear. Deleting a spam-flagged number mid-run breaks retries, and changing weights needs a terminate and restart | **Ishaan** (ops), Jagan (design) | Written runbook: "if a number is spam-flagged, change its weight to 0 → terminate and restart X". The backup numbers are pre-loaded and named |
| 4 | **Wrong cohort / no Diwali cohort file** | Plan says the best cohort is Diwali committed-but-unpaid, but Cohort v7 has only Janmashtami and Pitru Paksha. Segment counts were "coming by mail" | **ayushman** decides, **Ishaan** builds | A file per workflow (Hot/Warm/Cold/FUP) with counts, excluding: paid in Diwali, DND, random amounts, non-genuine, "claims paid", vendor base |
| 5 | **Dedup / externalWorkId reuse** | Pitru Paksha re-called duplicates. A reused `externalWorkId` from Diwali **silently skips** calls | **Ishaan** | Ishaan confirms dedup on phone10 is done, and that `externalWorkId` has a new Kartik prefix |
| 6 | **Seva/benefit list not frozen** | Diwali changed 5→3 sevas at the last minute; `hot_wa_send` had "Annadana" hard-coded. Freeze asked in channel; no reply | **ayushman** (client), Harshdeep | Written freeze by Thu 19 Nov: Annadaan + Gau Seva only, amounts, no Mahaprasadam/address ask. Link slugs match. Eval and WA template updated |
| 7 | **Payment link / Karix fallback chain** | P1 webhook, P2 IP whitelist, P3 "ownership from Karix", P4 RCS/SMS still pending (HTML 28 Oct, shown 18 Nov; **no owner named**). With no RCS delivered status, SMS never fires, and the SMS template pointed to the Diwali landing page, not the payment page (Jagan 31 Oct). WbizTool is wired as an automated fallback in the Hot/Warm workflows (Jagan 29 Oct, 2 Nov) with 1–2 numbers and a 150-message cap; a manual extra round was also sent | **Jagan** (integration), **ayushman** (Karix/HKM chase) | Test commit on the 21st: WA delivered + status visible. Known behaviour if WA fails. SMS points to the Kartik payment page. Wbiz numbers ≥2 `[confirm]` |
| 7b | **Diwali-specific wiring in links and the payment check** | Seva slugs are `*-diwali`, the paid-check counts only Diwali sevas / HKM's Diwali flag, links expired 8 Nov, and the pre-dial "festival window" check **fails closed** (Jagan 29 Oct; PP HTML). Without new Kartik settings, calls won't dial or payments won't attribute. The HKM site also caches link redirects | **Jagan** + HKM web team via **ayushman**. No owner today: assign one | New HKM Kartik seva pages and slugs, attribution rule, link expiry and festival window, all set. Test payment on the 21st shows on the dashboard as Kartik |
| 8 | **Business hours default (19:00) / numbers not linked to follow-up agent** | Recurred in Janmashtami and Pitru Paksha. Pitru Paksha follow-up agent had no number | **Ishaan** | Screenshot of business hours on every number, 08:00–21:00, taken on the 21st after final config |
| 9 | **Config drift between the three bots** | Wrong LLM on Diwali bots, AMD off, Marathi stack wrong, different TTS version on the follow-up bot | **Swathi** | One table: bot × (LLM, fallback, STT, TTS model + voice "Gopal", AMD, 180 s cap, end-call, languages) all identical except the script |
| 10 | **Dashboard single point of failure** | Only Jagan knows it. Data source unknown. Spend must include Karix cost | **Harshdeep** → Jagan | Name a backup person. Data source written down. Spend formula agreed (calls × rate + Karix) |

| 11 | **Vendor leads leaking into the upload** | 50K of the 5L vendor base were already sent to Ishaan (18 Nov). You excluded the vendor base for Kartik | **Ishaan**, check by Harshdeep | Upload file's source column / count reconciles to the ISKCON base only |
| 12 | **Pressure to overspend** | ayushman said he is covering a ~₹1.5L revenue shortfall elsewhere and uses ISKCON to "fill up". Expect pushes for extra cold or evening batches beyond ₹2L | **You** | 17:00 go/no-go and any extra batch need your written OK. Stop-loss agreed in writing beforehand |
| 13 | **Ops staffing** | Ishaan is part-time (also on Credit Saison). Your 18 Nov 12:49 question to Jagan about FDE staffing has no reply. The follow-up seva-slug mapping (asked 29 Oct) has no owner since Aayush left | **Jagan / Tanmay** | Named owner for each launch-day ops step and a named backup |

Also watch:
- **180 s hard cut** can land mid-sentence and give a double "Hare Krishna". Nobody has checked the share of calls above 180 s; ask Swathi to pull it from the Diwali data.
- **HKM link-redirect cache** still open.
- **Retry-node bug** (Axio, 13 Oct): after the daily cap, the next retry lands at the same clock time next day, not at the start of business hours.
- **Vobiz ₹3.45L renewal dispute** with Akshay is still open.
- **ISKCON secrets in Slack** in plain text (Diwali dashboard password and API key).

---

## 1. Day-by-day checklist

### Thu 19 Nov — freeze day
- [ ] **ayushman:** seva/benefit list frozen in writing (Annadaan, Gau Seva, amounts, minimum ₹500?). So far it is only his verbal "tomorrow itself" on 18 Nov; your 14:26 Slack ask has no reply.
- [ ] **ayushman:** confirm which date is the actual festival: approval was "for 24th", and your 09:09 question on whether it is the Deepotsav ending on the 24th is unanswered. Also confirm which bot runs which day (22, 23, 24).
  - The 17 Nov plan: Bot 1 "is coming", Bot 2 same-day "is here", Bot 3 follow-up.
  - Not resolved on 18 Nov.
- [ ] **ayushman:** lead-split mail with counts per workflow, and the total lead count with its reasoning. You challenged the 30K/50K lead count on 18 Nov: ₹2L budget ÷ ~₹1.65 per call (₹33K per 20K calls) ≈ 1.2L call attempts ≈ ~40K leads at 3 retries.
- [ ] **Harshdeep:** provisioning heads-up to **Vivek, Prashant, Chetan, cc Abhishek Ranjan**, with volume per slot (8–11 AM, 7–9 PM) and dates.
- [ ] **Swathi:** bots shared. The 17 Nov call said "will **try** to share by the 19th", with the speaker unclear, so lock the date with her. Send her the §2 verification list *with* the handover.
- [ ] **Swathi:** share the Diwali good/bad call sheet.
- [ ] **Harshdeep → Jagan:** dashboard data source; Karix cost feed; backup person.
- [ ] **You:** agree the stop-loss with Tanmay/ayushman now: ₹50K spent with no ROAS → pause is not an "agent was bad" escalation.

### Fri 20 Nov — build verification
- [ ] Run §2 (agent) and §3 (TTS) yourself on every bot, in Hindi and English.
- [ ] Testers booked:
  - Telugu (Chenna Keshav), Kannada (Nidhishree), Marathi (Bhavana), Tamil (Gokulram).
  - **Tamil was not mentioned on 18 Nov, so check whether Tamil leads exist.**
  - Gujarati only if leads exist.
- [ ] **Ishaan:** dedup + normalisation done; new `externalWorkId` prefix; holdouts removed.
- [ ] **Ishaan:** names normalised; initials dropped; "devotee" fallback; zero "anonymous".
- [ ] **Jagan/ayushman:** Karix P1/P2/P4 status in writing. If still pending, write down the fallback (Wbiz numbers, manual SMS).

### Sat 21 Nov — dress rehearsal
- [ ] Upload ramp: 1 → 20 → 200 to the **test** segment only. Never upload to the follow-up workflow.
- [ ] End-to-end test with a real ₹ payment:
  - call → commit → WA link delivered → pay → dashboard shows it within ~10 s → follow-up suppressed.
  - Second test: commit, don't pay → follow-up queued at +24 h.
- [ ] Screenshots:
  - business hours per number
  - number weights (primary 33 / backup 1)
  - agent linked on all 4 workflows, follow-up agent included
  - CPS acknowledgement from Vivek
- [ ] Bot sign-off: Harshdeep (Hindi/English) + per-language testers. Mukund won't test, so this is the only gate.
- [ ] Write the **kill-switch runbook**: who pauses which workflow, and how (business hours → pause → delink numbers).

### Sun 22 Nov — launch
- 07:45:
  - Vivek online and watching #bm-telephony-alerts.
  - Push about 20K morning leads.
  - Hot first, then Warm. Cold only if Hot/Warm cleared and ROAS is OK.
- 08:00–08:15 — first 200 calls:
  - check failed/429 count
  - check the 0–30 s drop rate
  - listen to 5 recordings: greeting pronunciation, amount, link sent
- 11:00 — morning WhatsApp report to the client group: Donation / Spend / ROAS.
- 11:00–17:00 — watch payments trickle in.
  - Recall: ~1× on the day tends to end at ~1.7× after late payments.
  - **If spend ≥ ₹50K and no ROAS, stop.**
- 17:00 — go/no-go for the evening batch (7–9 PM; CPS is better then). ayushman makes the call; you sign off.
- 21:00–21:30 — evening report. Then confirm calls actually stopped (no queue bleed after hours).

### Mon 23 – Tue 24 Nov
- Same rhythm.
- Follow-up workflow fires 24 h after each commitment.
- WbizTool personal nudges to committed-but-unpaid (manual, ≤150 per number).
- 24 Nov night: delink numbers, turn inbound off, terminate workflows. Janmashtami left workflows live after the campaign.

### Wed 25 Nov — close-out
- [ ] Completion report:
  - funnel: attempts → connects → commitments → links delivered → paid
  - ROAS by segment
  - follow-up ROAS
  - Karix delivery %
  - incidents
- [ ] Reconcile with the client's Razorpay view.
- [ ] Release CPS back to Vivek.
- [ ] Book Dec/New Year must-dos: rotation-and-retry outside the workflow (Tanmay), Karix P1–P4, Diwali/Kartik cohort refresh, dashboard backup.

---

## 2. Agent verification list for Swathi's bots (run on each of the 3 bots)
**Script and flow**
- [ ] Festival copy correct per bot ("is coming" vs "is here"). **No Diwali, Pitru Paksha or Janmashtami leftovers anywhere**, including the English prompt, eval and WA template. This bit the Diwali bots.
- [ ] Sevas: Annadaan + Gau Seva only. **No Mahaprasadam.** If asked for an address: "a temple devotee will reach out".
- [ ] Amount ladder matches the agreed rule:
  - Hot/committed: last amount, or the step-up.
  - Warm: previous amount.
  - Cold: ₹1,501-style ask → step down.
  - Never below the client minimum `[confirm ₹500]`.
  - No re-asking the amount after a yes.
- [ ] After a yes: `send_donation_link` called **once**, confirmation spoken, no "pay later" loop, no repeated WA check.
- [ ] End-call fires on every branch (decline, voicemail, done) in all bots, follow-up included.
- [ ] 180 s cap set; closing line lands before the cut (test a long call).
- [ ] Caller identity: "ISKCON Hyderabad"-style name, spoken correctly.
- [ ] Voice: male "Gopal"; same TTS model and version on main and follow-up.
- [ ] LLM and fallback, STT (Saaras), AMD ON, reasoning effort, language stack per language. Copy the Diwali bot settings that worked; no new experiments.
- [ ] Language: mirrors the devotee. No Telugu↔English flip-flop. No "can you hear me" loop.
- [ ] Eval/disposition fields map to the 4 workflows; random amounts (>₹25K / <₹100) flagged, not counted as commitments.

**Data → speech**
- [ ] Name variable: initials dropped, script-converted for Telugu/Kannada/Tamil, "devotee" fallback.
- [ ] Amount variable passed as words in the call language (or spoken from turn 2).
- [ ] Seva variable is a display name, not a slug.

## 3. TTS pronunciation test script (record one call per language)
Say or force each of these and listen:
- इस्कॉन (ISKCON)
- हरे कृष्ण (Hare Krishna) — opening and closing
- सेवा, अन्नदान, गौ सेवा
- कार्तिक पूर्णिमा (Kartik Purnima)
- the amounts ₹501 / ₹1,008 / ₹1,501 / ₹2,508 / ₹5,008
- a name with initials (e.g. "A B C Kumar")
- the temple name

**Fail** if any of these happen:
- a word is spelled letter by letter
- "Hair / HAARE"
- an English-accented Sanskrit word in a regional call
- an amount in the wrong language
- a slug read aloud

**Root-cause rule:** fix it at the source. The LLM output, first message and variables must use Devanagari or lowercase; never all caps. Don't rely only on the console pronunciation dictionary: the Diwali ISKCON fix was a dictionary entry that was never retested.

## 4. Metrics to watch (Aayush/ayushman's frame from 18 Nov)
- **Input metrics:** attempts, connects / connect %, CPS per number vs cap (43), failed/429 count, 0–30 s drop %, telephony health, billing minutes.
- **Output metrics:** commitments, WA delivered % (~80% expected), read %, payments, ₹ donated, spend (calls + Karix), ROAS by segment, follow-up ROAS.
- **Client output:** two WhatsApp messages a day, three lines each.

## 5. Contradictions to settle before launch
1. Lead CSV access: the transcript shows ayushman + Ishaan hold it (data was passed to Aayush last time). Harshdeep and you are to be added. The Granola summary saying "Harshdeep + Ishaan" is wrong.
1b. Diwali final numbers (₹3,25,173 / ₹2,06,550 / 212 payments) come only from the meeting summary of a dashboard screenshot. Get the screenshot before quoting them.
2. Number pool. Plivo 3 / Vobiz 1, or the reverse? How many on follow-up?
3. Follow-up trigger: 24 h (practice) vs 4 h (workflow HTML).
4. Evening window: 5–9, 6–9 or 7–9 PM.
5. Hot vs Warm definitions: Tanmay's doc vs the 18 Nov meeting.
6. Lead count: 20K / 30K / 50K.
7. In-call payment: Pitru Paksha saw ~50% paid on call, but it's now dropped because of 2–7 min link latency. Confirm it's intentional.
8. Follow-up ROAS 13× vs 8.63× (for the report narrative).

## 6. Not built yet, and nobody should claim it is
- Number rotation + retry outside the workflow (Tanmay). **Not done.**
- Karix WA-status webhook (P1), IP whitelist (P2), Karix ownership (P3), RCS→SMS fallback (P4). **Pending**, no owner named.
- WbizTool **is** wired as a fallback in Hot/Warm (Jagan, 29 Oct), but only 1–2 numbers. Don't scale it.
- Auto-DND. Only built for Muthoot; no ISKCON evidence.
- Nautilus **lead store** / CRM. **Not done.** Nautilus is used only for the web-payment check.
- Failed-call status filter and duplicate UI (Vivek, "next release"). Unconfirmed.
- No-audio fix (~0.5% of calls, Janmashtami). Unconfirmed.
