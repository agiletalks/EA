const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const BASE_DIR = __dirname;

// Layer 1: HTTP Basic Authentication Credentials
const AUTH_USER = 'aigility-2026';
const AUTH_PASS = '24721942@Ai';
const EXPECTED_AUTH = 'Basic ' + Buffer.from(`${AUTH_USER}:${AUTH_PASS}`).toString('base64');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.mp4': 'video/mp4',
  '.m4a': 'audio/mp4',
  '.mp3': 'audio/mpeg',
  '.vtt': 'text/vtt; charset=utf-8',
  '.srt': 'text/plain; charset=utf-8'
};

const server = http.createServer((req, res) => {
  // Layer 1: HTTP Basic Auth Verification
  const authHeader = req.headers['authorization'];
  if (!authHeader || authHeader !== EXPECTED_AUTH) {
    res.writeHead(401, {
      'WWW-Authenticate': 'Basic realm="Emotional Agility Workshop Platform"',
      'Content-Type': 'text/html; charset=utf-8'
    });
    res.end('<h1>401 Unauthorized</h1><p>未授權訪問：請輸入講師認證帳號與密碼。</p>');
    return;
  }

  // Parse URL
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
  let pathname = decodeURIComponent(parsedUrl.pathname);

  if (pathname === '/' || pathname === '') {
    pathname = '/index.html';
  }

  let filePath;
  if (pathname.startsWith('/slides_extracted/')) {
    filePath = path.join(BASE_DIR, pathname);
  } else if (pathname.startsWith('/media/')) {
    filePath = path.join(BASE_DIR, pathname);
  } else {
    filePath = path.join(BASE_DIR, 'web_app', pathname);
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end(`404 Not Found: ${pathname}`);
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    // Support HTTP Range requests for video/audio streaming
    const range = req.headers.range;
    if (range && (ext === '.mp4' || ext === '.m4a' || ext === '.mp3')) {
      const parts = range.replace(/bytes=/, '').split('-');
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : stats.size - 1;
      const chunksize = end - start + 1;

      const fileStream = fs.createReadStream(filePath, { start, end });
      res.writeHead(206, {
        'Content-Range': `bytes ${start}-${end}/${stats.size}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunksize,
        'Content-Type': contentType,
        'Access-Control-Allow-Origin': '*'
      });
      fileStream.pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Length': stats.size,
        'Content-Type': contentType,
        'Accept-Ranges': 'bytes',
        'Cache-Control': 'no-cache',
        'Access-Control-Allow-Origin': '*'
      });
      fs.createReadStream(filePath).pipe(res);
    }
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`\n======================================================`);
  console.log(`  Emotional Agility Interactive Platform Server Ready!`);
  console.log(`  URL: http://127.0.0.1:${PORT}`);
  console.log(`======================================================\n`);
});
