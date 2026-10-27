import {continueRender, delayRender, staticFile} from 'remotion';

// Brand fonts loaded from public/fonts so every render uses them, not a system fallback.
const faces: [string, string, string][] = [
  ['Manrope', '500', 'ManropeM.ttf'], ['Manrope', '700', 'ManropeB.ttf'], ['Manrope', '800', 'ManropeXB.ttf'],
  ['Plex', '700', 'IBMPlexMono-Bold.ttf'],
];
const handle = delayRender('Loading fonts');
export const fontsReady: Promise<unknown> = Promise.all(faces.map(([family, weight, file]) => {
  const f = new FontFace(family, `url(${staticFile('fonts/' + file)})`, {weight});
  document.fonts.add(f);
  return f.load();
}));
fontsReady.then(() => continueRender(handle));
