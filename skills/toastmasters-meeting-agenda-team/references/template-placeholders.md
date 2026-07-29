# Packaged Template Placeholders

Use this mapping only with the four DOCX files in `assets/`. Replace every
occurrence of each token, including repeated header and footer occurrences.
Preserve the token's existing run, paragraph, table-cell, and hyperlink
formatting.

The templates are sample layouts, not content authorities. Apply
`agenda-requirements.md` first when a sample label or row conflicts with the
approved meeting sequence.

## Club and meeting details

| Token | Required value |
| --- | --- |
| `{Club}` | Club name |
| `{No}` | Club number |
| `{Theme}` | Meeting theme |
| `{Date}` | Meeting date in the club's preferred display format |
| `{Days}` | Recurring meeting day or cadence |
| `{Start}` | Approved meeting start time; also the first agenda-row time |
| `{End}` | Approved meeting end time and adjournment time |
| `{Website}` | Club website label and external hyperlink target |

For `{Website}`, update both visible text and the underlying external hyperlink.
Do not leave the template's sample URL as the link target.

## Club officers

| Token | Required value |
| --- | --- |
| `{Pres}` | Club President |
| `{VPE}` | Vice President Education |
| `{VPM}` | Vice President Membership |
| `{VPPR}` | Vice President Public Relations |
| `{Sec}` | Secretary |
| `{Treas}` | Treasurer |
| `{SAA}` | Sergeant at Arms |

Officer fields are optional only when the user approves their omission or an
explicit `TBD`. Remove the corresponding label/value cleanly when omission is
approved; do not leave an empty brace token.

## Meeting roles

| Token | Required value |
| --- | --- |
| `{Chair}` | Meeting chair or presiding officer |
| `{Inv}` | Invocation and pledge role holder |
| `{Guest}` | Guest-welcome role holder |
| `{TM}` | Toastmaster of the Day or Evening |
| `{Joke}` | Joke Master |
| `{Ah}` | Ah-Counter |
| `{Gram}` | Grammarian |
| `{Timer}` | Timer |
| `{GE}` | General Evaluator |
| `{Topics}` | Topicsmaster |

Treat invocation, guest welcome, and Joke Master as optional only when the
approved meeting plan omits them. The meeting-role introduction block must still
follow `agenda-requirements.md`; do not keep Individual Evaluator rows inside
that block merely because the packaged template contains sample evaluator rows.

## Speakers and evaluators

| Token | Required value |
| --- | --- |
| `{Spkr1}` | First speaker |
| `{Spkr2}` | Second speaker |
| `{Spkr3}` | Third speaker |
| `{Eval1}` | Evaluator paired with the first speaker |
| `{Eval2}` | Evaluator paired with the second speaker |
| `{Eval3}` | Evaluator paired with the third speaker |
| `{S1 time}` | First speech timing range |
| `{S2 time}` | Second speech timing range |
| `{S3 time}` | Third speech timing range |
| `{E1 time}` | First evaluation timing range |
| `{E2 time}` | Second evaluation timing range |
| `{E3 time}` | Third evaluation timing range |

The three packaged rows are sample capacity, not a limit. For additional
speaker/evaluator pairs, clone the nearest complete row and populate the added
editable text directly. Preserve numbering, timing, pairing, columns, borders,
fills, typography, alignment, and spacing. Do not invent unsupported brace
tokens or overwrite an existing participant.

## Calculated agenda times

| Token | Start time of |
| --- | --- |
| `{T1}` | Chair introduces the Toastmaster |
| `{T2}` | Toastmaster begins the meeting-role introduction block |
| `{T3}` | Separate Individual Evaluator introduction followed by Prepared Speeches |
| `{T4}` | Table Topics |
| `{T5}` | Toastmaster introduces the General Evaluator |
| `{T6}` | General Evaluator begins individual speech evaluations |
| `{T7}` | General Evaluator begins the functionary-report sequence |
| `{T8}` | General Evaluator's overall meeting report |
| `{T9}` | Awards |
| `{T10}` | Club business and closing announcements |

Calculate `{T1}` through `{T10}` chronologically from `{Start}` plus the
approved durations of every preceding row, including optional activities that
remain in the meeting. Use the approved one-minute Individual Evaluator
introduction immediately before Prepared Speeches. Keep Timer Report
second-to-last and General Evaluator Report last in the report sequence.

If any calculated time would exceed `{End}`, stop before document production,
report the overrun, and ask the user what to change. Do not compress or remove a
required session silently.

## Completion check

Before review:

1. Search the entire document for left and right brace characters and resolve
   every remaining token.
2. Verify repeated club, officer, schedule, and website fields agree everywhere.
3. Verify speaker/evaluator row counts and pairings against the production brief.
4. Recalculate `{Start}`, `{T1}` through `{T10}`, and `{End}` from the final rows.
5. Confirm the visible website label and hyperlink target both use `{Website}`.
