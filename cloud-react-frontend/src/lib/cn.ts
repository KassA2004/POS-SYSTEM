import { clsx, type ClassValue } from 'clsx';
import { extendTailwindMerge } from 'tailwind-merge';

/**
 * The design system registers a custom type scale (`--text-micro`, `--text-body`,
 * `--text-h1`, ...). tailwind-merge does not know these names, so by default it
 * classifies `text-body` as a *colour* utility. That puts it in the same conflict
 * group as `text-ink-inverse`, and the last class wins — silently deleting the
 * button's text colour and leaving black-on-black.
 *
 * Registering the scale under `font-size` keeps colour and size in separate
 * groups so both survive the merge.
 */
const FONT_SIZES = ['micro', 'caption', 'body', 'body-sm', 'lead', 'h1', 'h2', 'h3', 'display'];

const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      'font-size': [{ text: FONT_SIZES }],
    },
  },
});

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
