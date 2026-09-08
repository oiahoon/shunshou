const status = document.querySelector('#action-status');
const copyButton = document.querySelector('#copy-site');
copyButton?.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText('https://shunshou.miaowu.org/');
    status.textContent = '安装页链接已复制，可以发送到你的 iPhone。';
  } catch {
    status.textContent = '无法自动复制。安装页地址：https://shunshou.miaowu.org/';
  }
});
document.querySelectorAll('[data-download]').forEach(link => {
  link.addEventListener('click', () => {
    status.textContent = '请在「文件」的下载项中打开捷径；未出现文件时，请使用 Safari 重试。';
  });
});
