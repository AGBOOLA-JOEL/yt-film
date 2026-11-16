# Contributing to yt-film

Thanks for using yt-film. The repository is **public and source-available** (see [LICENSE](LICENSE)): anyone can
install it, use it for their own videos, report problems and suggest ideas. **Code changes are made by invited
collaborators only**, so pull requests from other accounts are turned off.

## How you can help
| You want to... | Do this |
|---|---|
| report something broken | open an issue with the **Bug report** form |
| ask for a feature, a new look, format or effect | open an issue with the **Feature or idea** form |
| share a film, a style, a look.json or a shots trick | open an issue with **Show and tell** (a link or a few stills) |
| ask how to do something | open a **Question** issue, or check the guides in `references/` first |
| report a security problem (a leaked key, a way to run code you didn't intend) | see [SECURITY.md](SECURITY.md); don't post it publicly |

A good bug report includes:
- your system (Mac / Windows / Linux, RAM) and how you installed;
- the output of `python scripts/doctor.py`;
- the exact command and the last 30 lines of its output (or `renders/bN.log`);
- a stills sheet (`python tools/stills.py bN`) if it's about how something looks.

Never paste your `.env`, API keys, or private images you don't want public.

## Suggesting code
If you've fixed something in your own copy, describe the change in an issue and paste the relevant lines or a diff
in a code block. A collaborator will review it and, if it fits, bring it into the repository (credited in the
commit). By posting it you agree to the contribution terms in the [LICENSE](LICENSE) (section 5).

## For collaborators
- Branch from `main`, keep one change per pull request, and fill in the pull request template.
- Engine changes: run `python tools/stills.py` on the Chadwick example (or the illustration reel) and attach the sheet.
- Keep the docs in step: SKILL.md, README.md and the relevant file in `references/`.
- No personal data, channel names, API keys or local paths in commits.

## Conduct
Be kind and specific. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
