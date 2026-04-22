// ===============================
// LOBSTER SYSTEM V2（進化版架構）
// 功能：
// 1. 每日固定 seed（可重現）
// 2. A/B 版本輸出
// 3. 權重選擇（熱門句更常出現）
// 4. 同時輸出 html + data.json
// ===============================

const fs = require('fs');

// ===== 基礎內容庫 =====
const hooks = [
  { text: "你以為你累，是因為工作多？", weight: 5 },
  { text: "你不是沒效率，是環境在拖你", weight: 4 },
  { text: "90%的人忽略了空間影響", weight: 3 },
  { text: "問題不在你，在你待的地方", weight: 5 }
];

const punches = [
  { text: "錯", weight: 5 },
  { text: "不是這樣", weight: 3 },
  { text: "你被誤導了", weight: 4 }
];

const truths = [
  { text: "空間會慢慢影響你的決策", weight: 5 },
  { text: "壓力環境會降低專注力", weight: 4 },
  { text: "缺乏自然元素會讓人疲勞", weight: 5 }
];

// ===== seed（讓每天穩定但可變） =====
function getSeed(){
  return new Date().toDateString();
}

function seededRandom(seed){
  let x = 0;
  for(let i=0;i<seed.length;i++) x += seed.charCodeAt(i);
  return function(){
    x = (x * 9301 + 49297) % 233280;
    return x / 233280;
  }
}

// ===== weighted pick =====
function pick(list, rand){
  const total = list.reduce((a,b)=>a+b.weight,0);
  let r = rand() * total;
  for(const item of list){
    r -= item.weight;
    if(r <= 0) return item.text;
  }
  return list[0].text;
}

// ===== 產生版本 =====
function generateVersion(version, rand){
  const h = pick(hooks, rand);
  const p = pick(punches, rand);
  const t = pick(truths, rand);

  return `
  <div class="sec">${h}</div>
  <div class="sec">${p}</div>
  <div class="sec">${t}</div>
  <div class="sec">你以為是能力問題，其實是環境問題</div>
  <div class="sec">
    <a href="truth.html">了解真相</a>
  </div>
  `;
}

// ===== 主生成 =====
function build(){
  const seed = getSeed();
  const rand = seededRandom(seed);

  const v1 = generateVersion("A", rand);
  const v2 = generateVersion("B", rand);

  const html = `
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>龍蝦老師 V2</title>
<style>
body{margin:0;background:#020617;color:#fff;font-family:sans-serif;overflow-x:hidden}
.sec{height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;font-size:2rem;padding:20px}
.tabs{position:fixed;top:10px;left:10px}
button{margin:5px;padding:8px 12px}
</style>
</head>
<body>

<div class="tabs">
<button onclick="show('a')">A版</button>
<button onclick="show('b')">B版</button>
</div>

<div id="a">
${v1}
</div>

<div id="b" style="display:none">
${v2}
</div>

<script>
function show(v){
  document.getElementById('a').style.display = v==='a'?'block':'none';
  document.getElementById('b').style.display = v==='b'?'block':'none';
}
</script>

</body>
</html>
`;

  fs.writeFileSync('lobster.html', html);

  fs.writeFileSync('data.json', JSON.stringify({
    date: seed,
    version: "v2"
  }, null, 2));

  console.log("✅ V2 生成完成", seed);
}

build();
