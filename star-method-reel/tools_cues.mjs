// prints the caption cues as JSON for srt.py (same numbers the page uses)
import { readFileSync } from 'fs';
const film = await import('./film.js');
film.setup(JSON.parse(readFileSync(new URL('./voices/dur.json', import.meta.url))));
console.log(JSON.stringify(film.cues().map(c => ({ t0: c.t0, t1: c.t1, text: c.text }))));
