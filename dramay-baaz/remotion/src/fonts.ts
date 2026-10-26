import {continueRender, delayRender, staticFile} from 'remotion';

// Brand font (Manrope) loaded from public/fonts so every render uses it, not a system fallback.
const faces: [string, string][] = [['500', 'ManropeM.ttf'], ['700', 'ManropeB.ttf'], ['800', 'ManropeXB.ttf']];
const extra = [new FontFace('Plex', `url(${staticFile('fonts/IBMPlexMono-Bold.ttf')})`, {weight: '700'})];
extra.forEach((f) => document.fonts.add(f));
const handle = delayRender('Loading Manrope');
Promise.all(faces.map(([weight, file]) => {
  const f = new FontFace('Manrope', `url(${staticFile('fonts/' + file)})`, {weight});
  document.fonts.add(f);
  return f.load();
}).concat(extra.map((f) => f.load()))).then(() => continueRender(handle));
