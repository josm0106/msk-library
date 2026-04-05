import re, sys

src = r'C:\xampp\htdocs\mysite\index.html'
dst = r'C:\xampp\htdocs\mysite\msk-library-temp\index.html'

with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add login CSS before </style>
login_css = """
/* Login Screen */
#loginScreen{position:fixed;top:0;left:0;width:100%;height:100%;background:var(--bg);z-index:99999;display:flex;align-items:center;justify-content:center}
#loginScreen.hidden{display:none}
.login-box{background:var(--card);border:1px solid var(--bdr);border-radius:16px;padding:2.5rem;text-align:center;max-width:380px;width:90%}
.login-box h2{font-size:1.5rem;background:linear-gradient(135deg,var(--ac),#00f5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.5rem}
.login-box p{color:var(--tx2);font-size:.9rem;margin-bottom:1.5rem}
.login-box input{width:100%;padding:.75rem 1rem;background:var(--bg3);border:1px solid var(--bdr);border-radius:8px;color:var(--tx);font-size:1rem;text-align:center;margin-bottom:1rem}
.login-box input:focus{outline:none;border-color:var(--ac);box-shadow:0 0 8px rgba(0,212,255,.2)}
.login-box button{width:100%;padding:.75rem;background:linear-gradient(135deg,var(--ac),#00a8cc);border:none;border-radius:8px;color:#fff;font-size:1rem;font-weight:600;cursor:pointer;transition:opacity .3s}
.login-box button:hover{opacity:.85}
.login-err{color:var(--err);font-size:.85rem;margin-top:.5rem;min-height:1.2rem}
#mainContent{display:none}
#mainContent.show{display:block}"""

content = content.replace('</style>', login_css + '\n</style>')

# 2. Add login HTML after <body>
login_html = """
<div id="loginScreen">
<div class="login-box">
<h2>MSK Orthopedic Library</h2>
<p>\uc811\uadfc\uc774 \uc81c\ud55c\ub41c \uc0ac\uc774\ud2b8\uc785\ub2c8\ub2e4.<br>\ube44\ubc00\ubc88\ud638\ub97c \uc785\ub825\ud574\uc8fc\uc138\uc694.</p>
<input type="password" id="loginPw" placeholder="Password" autofocus>
<button onclick="checkLogin()">Enter</button>
<div class="login-err" id="loginErr"></div>
</div>
</div>
<script>
const PW_HASH='9466c70d025598f4dee0e4876b22886a72191a1e6521a7315c8abc3ad6c4ad11';
async function sha256(str){const buf=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(str));return[...new Uint8Array(buf)].map(b=>b.toString(16).padStart(2,'0')).join('')}
async function checkLogin(){
const pw=document.getElementById('loginPw').value;
const hash=await sha256(pw);
if(hash===PW_HASH){
sessionStorage.setItem('msk_auth','1');
document.getElementById('loginScreen').classList.add('hidden');
document.getElementById('mainContent').classList.add('show');
}else{document.getElementById('loginErr').textContent='\ube44\ubc00\ubc88\ud638\uac00 \ud2c0\ub838\uc2b5\ub2c8\ub2e4.';}
}
document.getElementById('loginPw').addEventListener('keydown',e=>{if(e.key==='Enter')checkLogin();});
if(sessionStorage.getItem('msk_auth')==='1'){document.getElementById('loginScreen').classList.add('hidden');document.addEventListener('DOMContentLoaded',()=>{document.getElementById('mainContent').classList.add('show');});}
</script>
<div id="mainContent">"""

content = content.replace('<body>\n<div id="topBar">', '<body>\n' + login_html + '\n<div id="topBar">')

# 3. Close mainContent div before </body>
content = content.replace('</body>', '</div><!-- end mainContent -->\n</body>')

with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Done! Output: {len(content)} bytes written to {dst}")
