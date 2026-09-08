import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
const require = createRequire(new URL('../prototypes/shunshou/package.json', import.meta.url));
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const icons = require('@radix-ui/react-icons');
const selected = {
  'arrow-up-right': 'ArrowTopRightIcon', 'arrow-down': 'ArrowDownIcon',
  'arrow-right': 'ArrowRightIcon', 'arrow-left': 'ArrowLeftIcon',
  copy: 'CopyIcon', check: 'CheckIcon', github: 'GitHubLogoIcon',
  lock: 'LockClosedIcon', download: 'DownloadIcon', play: 'PlayIcon',
  share: 'Share1Icon', close: 'Cross2Icon', plus: 'PlusIcon',
};
const symbols = Object.entries(selected).map(([id, name]) =>
  `<symbol id="${id}" viewBox="0 0 24 24">${renderToStaticMarkup(React.createElement(icons[name], { width: 24, height: 24 }))}</symbol>`).join('');
const dir = new URL('../services/resolver/public/assets/', import.meta.url);
mkdirSync(dir, { recursive: true });
writeFileSync(new URL('icons.svg', dir), `<svg xmlns="http://www.w3.org/2000/svg">${symbols}</svg>`);
const arrow = renderToStaticMarkup(React.createElement(icons.ArrowTopRightIcon, { width: 44, height: 44, color: '#ffcc29' }));
writeFileSync(new URL('favicon.svg', dir), `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#101010"/><g transform="translate(10 10)">${arrow}</g></svg>`);
