# CLLTE Car Seat -- Kolton

A standalone, real-time speech shadow and predictive echolalia companion,
built for Kolton. This is the "Project SOAR" engine, split out on its own so
it can run on his machine without any of Collette's other projects,
background tasks, or unrelated data attached to it.

It listens continuously while he talks, predicts the next few words he's
reaching for, and speaks them back through ElevenLabs -- adapting its style
to whether he's calm, stuck, or frustrated in the moment. Full detail on the
loop, the controls (F7 kill switch, silence handling, auto-sleep, echo
guard), and the tuning knobs is in [carseat/README.md](carseat/README.md).

## First-time setup

1. Install Python 3.11+.
2. `pip install -r requirements.txt`
3. `copy carseat\.env.example carseat\.env` and fill in the real API keys
   (ElevenLabs voice ID + key, OpenRouter key). **Never commit `carseat/.env`**
   -- it's already gitignored.
4. Double-click `run_carseat.bat`, or run `python -m carseat.server` from
   this folder.
5. Open http://127.0.0.1:8001 in a browser, allow microphone access, and
   click Start.

## Where this came from

This is a split-off, standalone copy of the `carseat/` engine built inside
[CLLTERaceCarSeat](https://github.com/sashafwolf/CLLTERaceCarSeat), Sasha's
household bundle repo for Collette. That repo also carries her full soul
(Discord/Twitch/Dominion/RaceBrain), which Kolton doesn't need and shouldn't
have to run just to get this. Everything in this repo is self-contained --
no imports reach back into that bundle.

If the engine itself changes (prediction prompt, emotion heuristics, the
audio pipeline), pull the update from there; this repo won't get those
changes automatically.
