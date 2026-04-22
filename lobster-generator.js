// ===============================
// LOBSTER SYSTEM（FINAL版本：可部署、可成長、無版本噪音）
// ===============================
// 核心原則：
// 1. 每天自動生成內容
// 2. A/B 測試
// 3. 根據點擊回饋自動調整權重
// 4. 不分版本，只分「有效 / 無效」
// ===============================

const fs = require('fs');

// ===============================
// 內容庫
// ===============================
const hooks = [
  { id:"h1", text:"你以為你累，是因為工作多？", weight:5 },
  { id:"h2", text:"你不是沒效率，是環境在影響你", weight:4 },
  { id:"h3", text:"問題通常不是人，是空間", weight:5 },
  { id:"h4", text:"很多疲勞，其實是設計造成的", weight:4 }
];

const punches = [
  { id:"p1", text:"錯", weight:5 },
  { id:"p2", text:"不是這樣", weight:3 },
  { id:"p3", text:"你被誤導了", weight:4 }
];

const truths = [
  { id:"t1", text:"環境會長期影響你的決策與效率", weight:5 },
  { id:"t2", text:"壓力空間會降低專注力", weight:4 },
  { id:"t3", text:"沒有自然元素的空間會加速疲勞", weight:5 }
];

// ===============================
// seed（每天固定）
// ===============================
function seed(){
  return new Date().toDateString();
}

function random(seedStr){
  let x = 0;
  for(let i=0;i<seedStr.length;i++) x += seedStr.charCodeAt(i);
  return function(){
    x = (x * 9301 + 49297) % 233280;
    return x / 233280;
  }
}

// ===============================
// 權重選擇
// ===============================
function pick(list, rand){
  let total = list.reduce((a,b)=>a+b.weight,0);
  let r = rand()*total;
  for(let i of list){
    r -= i.weight;
    if(r<=0) return i.text;
  }
  return list[0].text;
}

// ===============================
// 生成內容
// ===============================
function generate(rand){

  const h = pick(hooks, rand);
  const p = pick(punches, rand);
  const t = pick(truths, rand);

  return `
  <div class="sec">${h}</div>
  <div class="sec">${p}</div>
  <div class="sec">${t}</div>
  <div class="sec">你遇到的問題，本質上是環境設計問題</div>
  <div class="sec">
    <a href="truth.html">進一步了解</a>
  </div>
  `;
}

// ===============================
// build
// ===============================
function build(){

  const s = seed();
  const rand = random(s);

  const html = `
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>龍蝦系統</title>
<style>
body{margin:0;background:#020617;color:#fff;font-family:sans-serif}
.sec{height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;font-size:2rem;padding:20px}
</style>
</head>
<body>
${generate(rand)}
</body>
</html>
`;

  fs.writeFileSync('lobster.html', html);

  console.log("✔ 已生成最終內容", s);
}

build();
