import { useState } from "react";
import { ArrowTopRightIcon, ArrowLeftIcon, ArrowRightIcon, CheckIcon, CopyIcon, QuestionMarkCircledIcon, ChevronDownIcon, Cross2Icon } from "@radix-ui/react-icons";
import { BottomSheet, MobileScroll } from "./mobile";

export default function Prototype() {
  const [sheet, setSheet] = useState<string | null>(null);
  const [quality, setQuality] = useState("优先 720p");
  const [cleanup, setCleanup] = useState(true);
  const [installed, setInstalled] = useState(false);
  const [connection, setConnection] = useState("未检测");
  const [copyStatus, setCopyStatus] = useState("");
  async function copyCode() {
    try { await navigator.clipboard.writeText("DEMO-ONLY-0000"); setCopyStatus("演示访问码已复制"); }
    catch { setCopyStatus("无法复制：DEMO-ONLY-0000"); }
  }
  return <><MobileScroll className="app-screen shunshou"><main className="setup">
    <header className="brand-row"><div className="brand"><span className="brand-mark" aria-hidden="true"><ArrowRightIcon/><ArrowLeftIcon/></span><span>顺手</span></div><button className="icon-button" aria-label="帮助" title="帮助" onClick={()=>setSheet("帮助")}><QuestionMarkCircledIcon/></button></header>
    <section className="intro"><p className="eyebrow">SETUP / {connection==="已连接"?"03":"02"}</p><h1>{connection==="已连接"?"连接就绪":"准备连接"}</h1></section>
    <ol className="steps">{[{label:"授权",done:true,status:"已获邀请"},{label:"安装",done:installed,status:installed?"已安装":"待进行"},{label:"检测",done:connection==="已连接",status:connection==="已连接"?"已连接":"待进行"}].map((step,i)=><li key={step.label}><span className="step-number">0{i+1}</span><span className="step-label">{step.label}</span><span className={`step-state ${step.done?"done":"pending"}`}>{step.done?<span className="check-disc"><CheckIcon/></span>:<span className="ring"/>}{step.status}</span></li>)}</ol>
    <section className="preferences" aria-label="连接设置"><div className="access"><h2>个人访问码</h2><div className="code-row"><span className="code-mask" aria-label="演示访问码已隐藏">{Array.from({length:8},(_,i)=><i key={i}/>)}</span><button className="copy-button" title="复制演示访问码" aria-label="复制演示访问码" onClick={copyCode}>{copyStatus.includes("已复制")?<CheckIcon/>:<CopyIcon/>}</button></div><span className="copy-status" role="status">{copyStatus}</span></div>
    <button className="setting-row" onClick={()=>setSheet("画质")}><span>画质</span><span className="setting-value">{quality}<ChevronDownIcon/></span></button>
    <div className="setting-row"><span>分享后清理</span><button className="toggle" role="switch" aria-checked={cleanup} aria-label="分享后清理" onClick={()=>setCleanup(!cleanup)}><span/></button></div></section>
    <button className="install-button" onClick={()=>setSheet("添加快捷指令")}><span>{installed?"查看快捷指令":"添加快捷指令"}</span><span className="install-arrow"><ArrowTopRightIcon/></span></button>
    <button className="connection-row" onClick={()=>setSheet("检查连接")}><span>检查连接</span><span className={connection==="已连接"?"done":"pending"}>{connection==="已连接"?<CheckIcon/>:<span className="ring"/>}{connection}</span></button>
    <footer><button onClick={()=>setSheet("隐私")}>隐私</button><span/><button onClick={()=>setSheet("帮助")}>帮助</button></footer>
  </main></MobileScroll>
  <BottomSheet open={sheet!==null} onOpenChange={open=>{if(!open)setSheet(null)}} title={sheet??""} snap={0.58}><div className="panel-body"><button className="panel-close icon-button" aria-label="关闭" onClick={()=>setSheet(null)}><Cross2Icon/></button>
    {sheet==="画质"&&<div className="quality-options">{["优先 720p","最高可用画质","节省流量"].map(q=><button key={q} aria-pressed={quality===q} onClick={()=>{setQuality(q);setSheet(null)}}><span>{q}</span>{quality===q&&<CheckIcon/>}</button>)}</div>}
    {sheet==="添加快捷指令"&&<><p className="panel-kicker">交互原型 · 非真实安装</p><p>正式版本将在 iOS 快捷指令中完成添加。当前不会安装快捷指令，也不会连接你的账号。</p><button className="panel-primary" onClick={()=>{setInstalled(true);setSheet(null)}}>模拟安装完成 <ArrowTopRightIcon/></button></>}
    {sheet==="检查连接"&&<><p className="panel-kicker">交互原型 · 模拟检测</p><p>{installed?"选择一个测试结果。此处不会发送网络请求，也不代表媒体已成功下载。":"请先完成模拟安装，再测试连接状态。"}</p><button className="panel-primary" disabled={!installed} onClick={()=>{setConnection("已连接");setSheet(null)}}>模拟连接成功 <CheckIcon/></button><button className="panel-secondary" disabled={!installed} onClick={()=>{setConnection("连接失败");setSheet(null)}}>模拟连接失败</button></>}
    {sheet==="隐私"&&<><p>演示访问码不具备任何权限。此原型不读取 Instagram 账号，不上传媒体，也不保存你的设置。</p><p>正式版的清理范围仅限本次下载的临时文件，不包含相册或原始文件。关闭分享面板不等于发送成功。</p></>}
    {sheet==="帮助"&&<><p className="panel-kicker">顺手 / 预览版</p><p>正式流程：获得邀请 → 添加快捷指令 → 检测连接。之后从 Instagram 分享菜单调用快捷指令。</p><p>本页的安装和检测均为模拟。真实服务、访问码授权及微信分享尚未接入。</p><button className="panel-secondary" onClick={()=>{setInstalled(false);setConnection("未检测");setQuality("优先 720p");setCleanup(true);setCopyStatus("");setSheet(null)}}>重置演示</button></>}
  </div></BottomSheet></>;
}
