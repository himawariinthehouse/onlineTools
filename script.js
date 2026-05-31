// 基础计算器
const display = document.getElementById('calcDisplay');
function append(val) { display.value += val; }
function clearDisplay() { display.value = ''; }
function calculate() {
  try {
    let expr = display.value.replace('×', '*').replace('÷', '/');
    display.value = eval(expr);
  } catch (e) {
    display.value = '错误';
  }
}

// BMI计算器
function calcBMI() {
  const h = document.getElementById('bmiHeight').value / 100;
  const w = document.getElementById('bmiWeight').value;
  if (!h || !w) return;
  const bmi = (w / (h * h)).toFixed(1);
  let status = '';
  if (bmi < 18.5) status = '偏瘦';
  else if (bmi < 24) status = '正常';
  else if (bmi < 28) status = '超重';
  else status = '肥胖';
  document.getElementById('bmiResult').textContent = `BMI: ${bmi} (${status})`;
}

// 房贷计算器
function calcLoan() {
  const p = parseFloat(document.getElementById('loanAmount').value);
  const r = parseFloat(document.getElementById('loanRate').value) / 100 / 12;
  const n = parseInt(document.getElementById('loanYears').value) * 12;
  if (!p || !r || !n) return;
  const emi = p * r * Math.pow(1 + r, n) / (Math.pow(1 + r, n) - 1);
  const total = (emi * n).toFixed(2);
  document.getElementById('loanResult').textContent = `月供: ${emi.toFixed(2)} 元 | 总还款: ${total} 元`;
}

// 单位换算
const unitFactors = {
  cm: 1, m: 100, km: 100000, in: 2.54, ft: 30.48
};
function convertUnit() {
  const val = parseFloat(document.getElementById('unitValue').value);
  const from = document.getElementById('unitFrom').value;
  const to = document.getElementById('unitTo').value;
  if (!val) return;
  const result = (val * unitFactors[from] / unitFactors[to]).toFixed(4);
  document.getElementById('unitResult').textContent = `${val} ${from} = ${result} ${to}`;
}

// 温度换算
function convertTemp() {
  const val = parseFloat(document.getElementById('tempValue').value);
  const from = document.getElementById('tempFrom').value;
  const to = document.getElementById('tempTo').value;
  if (!val) return;
  let c;
  if (from === 'c') c = val;
  else if (from === 'f') c = (val - 32) * 5/9;
  else c = val - 273.15;

  let result;
  if (to === 'c') result = c.toFixed(2);
  else if (to === 'f') result = (c * 9/5 + 32).toFixed(2);
  else result = (c + 273.15).toFixed(2);

  document.getElementById('tempResult').textContent = `${val}°${from.toUpperCase()} = ${result}°${to.toUpperCase()}`;
}

// 年龄计算器
function calcAge() {
  const birth = new Date(document.getElementById('birthDate').value);
  const now = new Date();
  if (isNaN(birth.getTime())) return;
  let age = now.getFullYear() - birth.getFullYear();
  const monthDiff = now.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < birth.getDate())) age--;
  document.getElementById('ageResult').textContent = `年龄: ${age} 岁`;
}