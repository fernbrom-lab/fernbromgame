// ===============================
// lobster-generator.js
// 每天自動生成一組龍蝦腳本（可直接輸出成 HTML）
// ===============================

const fs = require('fs');

const hooks = [
  "你以為你累，是因為工作多？",
  "你每天不舒服，其實不是你問題",
  "大多數辦公室，都在慢性傷害人",
  "你覺得效率低，其實是環境在拖垮你",
  "你公司花錢請人，卻忽略最關鍵的東西"
];

const punches = [
  "錯",
  "問題不在你",
  "這只是表象",
  "你被誤導了",
  "真正原因沒人講"
];

const truths = [
  "你的空間沒有自然元素",
  "長時間處在壓力視覺環境",
  "空氣品質與濕度失衡",
  "缺乏讓大腦放鬆的綠意",
  "環境設計根本沒考慮人"
];

function pick(arr){
  return arr[Math.floor(Math.random()*arr.length)];
}

function generateHTML(){
  const h = pick(hooks);
  const p = pick(punches);
  const t = pick(truths);

  return `<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>龍蝦老師</title>
<style>
body{margin:0;background:#020617;color:#fff;font-family:sans-serif}
.sec{height:100vh;display:flex;justify-content:center;align-items:center;text-align:center;padding:20px;font-size:2rem}
.btn{padding:15px 25px;background:#ef4444;border-radius:12px;cursor:pointer}
</style>
</head>
<body>

<div class="sec">${h}</div>
<div class="sec">${p}</div>
<div class="sec">${t}</div>
<div class="sec">你不是沒效率<br>你只是被環境消耗</div>
<div class="sec">
<div>
有些公司已經開始改
<br><br>
<div class="btn" onclick="location.href='truth.html'">他們怎麼做？</div>
</div>
</div>

</body>
</html>`;
}

fs.writeFileSync('lobster.html', generateHTML());
console.log('✅ 今日龍蝦腳本已生成');
