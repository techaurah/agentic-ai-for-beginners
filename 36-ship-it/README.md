# Lesson 36: Ship It

**Time:** 60-90 minutes · **Difficulty:** Intermediate · **Prerequisites:** Lessons 34 and 35 complete: a working, evaluated capstone

## The hook

An unshipped capstone is a rumour. It exists on your laptop, in your head, in a half-finished repo nobody can run. The last lesson of this course is the least technical and the most career-relevant: turning your build into a public, runnable, documented project, and submitting it to the course showcase where it becomes evidence. Evidence of skill is what gets developers hired and what gets companies trusted. This lesson is a checklist, a template, and a door. Walk through it.

## Step 1: the deployment checklist

"Deployed" for this capstone means: a stranger can clone your repo and run the whole system, offline, with the commands in your README, and get the output your README shows. Work down this list:

- [ ] **One-command run.** From a fresh clone, the demo runs with a single documented command. No undocumented setup, no "it works if you also" steps.
- [ ] **Zero credentials on the demo path.** Fake keys and seed data only. Anything real belongs behind the adapter seams and is described, not required.
- [ ] **Deterministic output.** Same input, same output. If any part is nondeterministic, the README says which part and why.
- [ ] **Eval suite wired in.** One command runs the harness; the output is pasted in the README and current.
- [ ] **No secrets, no personal data.** Search your repo for keys, tokens, real phone numbers, real customer names. Fictional data only, everywhere, including test fixtures and screenshots.
- [ ] **License file present.** MIT unless you have a reason; a repo without a license is legally closed by default, whatever you intended.
- [ ] **The production path is described, not faked.** Your README explains how the real calendar adapter and the real extractor would be wired, with the seam named. Nobody is fooled by a mock wearing a production costume, and the honest seam is the more impressive engineering.

If you later take a version of this system live for a real business, Module 9 is your checklist (deployment, observability, security, cost). The capstone's bar is lower and stricter at once: lower because nothing real is sent, stricter because everything claimed must be runnable by a stranger.

## Step 2: write the project README

Your project README is the most-read document you will produce in this course, and for many readers it is the whole interview. Use `project-readme-template.md` from this lesson. Its structure is deliberate:

1. **What it does, in one paragraph.** Plain language, the Brightpath brief named, the outcome stated. Fifteen seconds to comprehension.
2. **Demo, with real output.** Commands first, then the actual terminal output pasted in. Real output is unfakeable credibility; a screenshot of code is not.
3. **How it works.** The four stages, your extractor choice, state, idempotency, the full-calendar behaviour.
4. **Evaluation.** Harness output in full, plus your three added scenarios and what each protects.
5. **Design decisions and limits.** The honest section. What it does not do, where the seams are, what another week would add.
6. **Layout, license, credit.** A folder map, your license, and one line crediting the course with a link back.

Write the limits section like you mean it. Every strong engineering README you admired in this field has one. Reviewers, employers, and clients all read a candid limits list the same way: this person knows where their system ends. That is the person they want when the system has to grow.

## Step 3: submit to the showcase

The showcase is this course's completion artifact and its public leaderboard of finished work. Per the course CONTRIBUTING rules:

1. Make sure your project repo is public and passes the Step 1 checklist.
2. Fork the course repository.
3. Open `showcase/README.md`, read its row format (one row per learner: name or handle, project link, one-line description, eval score).
4. Add exactly one row for your project, in the position the format specifies. Touch nothing else in the file.
5. Open a pull request titled `Showcase: your project name`. In the PR body, link your repo and paste your harness summary line (for example, "11/11 scenarios passed, 8 shipped + 3 own").
6. Respond to review like a professional: maintainers check that the repo is public, the demo runs, and the eval output is present. Fix requests are normal; a merged row is the finish line.

Small fixes to the course itself (a typo, a broken link you spotted on the way) may go straight to a PR as their own change, per CONTRIBUTING. Do not bundle them into your showcase PR; one change per PR keeps review fast and your showcase row clean.

## Step 4: the completion self-check

Finish with `completion-checklist.md` from this lesson: copy it into your fork, check the boxes honestly, including the course-level ones, and read its closing note. There is no certificate for this course. What you hold instead is a public, evaluated, documented system and a merged showcase row. In a hiring conversation or a client meeting, that outperforms a PDF badge, because anyone can open it, run it, and read the eval output themselves.

Then do the thing that makes courses compound: tell people. A short post about what you built, what the eval suite caught, and what you would do next is worth more than the repo sitting quietly. Link the repo. Link the course. Other learners find both through you, which is how this ecosystem, and your reputation in it, actually grows.

## Common failures

- **Shipping the code without the demo output.** A README that claims behaviour it does not show asks for trust it has not earned.
- **The private repo.** A showcase row pointing at a 404 is worse than no row. Check visibility in a private browser window before submitting.
- **One giant PR.** Showcase row, three lesson fixes, and a translation in a single PR guarantees a slow review and a messy history.
- **Waiting for perfect.** The checklist is the bar, not flawlessness. Systems that pass it are finished. Ship, then improve in public, where improvements are visible too.

## Recap

Ship means: runnable by a stranger, honest in its README, evaluated in public, and listed in the showcase. You started this course with a definition of an agent. You end it with a working business assistant, an eval suite that proves what it does, a deployment checklist you can reuse on every future project, and a public artifact with your name on it. That is the whole promise of the course, kept. From here, the paths branch: deepen with the Academy's other courses, contribute fixes and scenarios back to this one, or take the Brightpath pattern into real client work, bought or built, with your eyes open. Good building.

## Resources

- The templates in this lesson: `project-readme-template.md`, `completion-checklist.md`
- The course CONTRIBUTING (two-tier rule, showcase row format lives in `showcase/README.md` at the course root): ../CONTRIBUTING.md
- GitHub, about READMEs and profile-quality project pages: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- GitHub, licensing a repository: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/about-licensing
- Choose a License (plain-language license picker, MIT first): https://choosealicense.com
