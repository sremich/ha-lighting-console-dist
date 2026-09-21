var Tt=Object.defineProperty;var Pt=Object.getOwnPropertyDescriptor;var m=(n,e,t,i)=>{for(var r=i>1?void 0:i?Pt(e,t):e,s=n.length-1,o;s>=0;s--)(o=n[s])&&(r=(i?o(e,t,r):o(r))||r);return i&&r&&Tt(e,t,r),r};var L=globalThis,j=L.ShadowRoot&&(L.ShadyCSS===void 0||L.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,K=Symbol(),lt=new WeakMap,P=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==K)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(j&&e===void 0){let i=t!==void 0&&t.length===1;i&&(e=lt.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&lt.set(t,e))}return e}toString(){return this.cssText}},ct=n=>new P(typeof n=="string"?n:n+"",void 0,K),M=(n,...e)=>{let t=n.length===1?n[0]:e.reduce((i,r,s)=>i+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+n[s+1],n[0]);return new P(t,n,K)},dt=(n,e)=>{if(j)n.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let i=document.createElement("style"),r=L.litNonce;r!==void 0&&i.setAttribute("nonce",r),i.textContent=t.cssText,n.appendChild(i)}},J=j?n=>n:n=>n instanceof CSSStyleSheet?(e=>{let t="";for(let i of e.cssRules)t+=i.cssText;return ct(t)})(n):n;var{is:Mt,defineProperty:Nt,getOwnPropertyDescriptor:Ht,getOwnPropertyNames:Ot,getOwnPropertySymbols:It,getPrototypeOf:Dt}=Object,q=globalThis,ht=q.trustedTypes,Ut=ht?ht.emptyScript:"",zt=q.reactiveElementPolyfillSupport,N=(n,e)=>n,H={toAttribute(n,e){switch(e){case Boolean:n=n?Ut:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,e){let t=n;switch(e){case Boolean:t=n!==null;break;case Number:t=n===null?null:Number(n);break;case Object:case Array:try{t=JSON.parse(n)}catch{t=null}}return t}},G=(n,e)=>!Mt(n,e),pt={attribute:!0,type:String,converter:H,reflect:!1,useDefault:!1,hasChanged:G};Symbol.metadata??=Symbol("metadata"),q.litPropertyMetadata??=new WeakMap;var y=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=pt){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let i=Symbol(),r=this.getPropertyDescriptor(e,i,t);r!==void 0&&Nt(this.prototype,e,r)}}static getPropertyDescriptor(e,t,i){let{get:r,set:s}=Ht(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:r,set(o){let l=r?.call(this);s?.call(this,o),this.requestUpdate(e,l,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??pt}static _$Ei(){if(this.hasOwnProperty(N("elementProperties")))return;let e=Dt(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(N("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(N("properties"))){let t=this.properties,i=[...Ot(t),...It(t)];for(let r of i)this.createProperty(r,t[r])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[i,r]of t)this.elementProperties.set(i,r)}this._$Eh=new Map;for(let[t,i]of this.elementProperties){let r=this._$Eu(t,i);r!==void 0&&this._$Eh.set(r,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let i=new Set(e.flat(1/0).reverse());for(let r of i)t.unshift(J(r))}else e!==void 0&&t.push(J(e));return t}static _$Eu(e,t){let i=t.attribute;return i===!1?void 0:typeof i=="string"?i:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return dt(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){let i=this.constructor.elementProperties.get(e),r=this.constructor._$Eu(e,i);if(r!==void 0&&i.reflect===!0){let s=(i.converter?.toAttribute!==void 0?i.converter:H).toAttribute(t,i.type);this._$Em=e,s==null?this.removeAttribute(r):this.setAttribute(r,s),this._$Em=null}}_$AK(e,t){let i=this.constructor,r=i._$Eh.get(e);if(r!==void 0&&this._$Em!==r){let s=i.getPropertyOptions(r),o=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:H;this._$Em=r;let l=o.fromAttribute(t,s.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(e,t,i,r=!1,s){if(e!==void 0){let o=this.constructor;if(r===!1&&(s=this[e]),i??=o.getPropertyOptions(e),!((i.hasChanged??G)(s,t)||i.useDefault&&i.reflect&&s===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,i))))return;this.C(e,t,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:r,wrapped:s},o){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,o??t??this[e]),s!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),r===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,s]of this._$Ep)this[r]=s;this._$Ep=void 0}let i=this.constructor.elementProperties;if(i.size>0)for(let[r,s]of i){let{wrapped:o}=s,l=this[r];o!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,s,l)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(t)):this._$EM()}catch(i){throw e=!1,this._$EM(),i}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};y.elementStyles=[],y.shadowRootOptions={mode:"open"},y[N("elementProperties")]=new Map,y[N("finalized")]=new Map,zt?.({ReactiveElement:y}),(q.reactiveElementVersions??=[]).push("2.1.2");var it=globalThis,ut=n=>n,F=it.trustedTypes,mt=F?F.createPolicy("lit-html",{createHTML:n=>n}):void 0,$t="$lit$",x=`lit$${Math.random().toFixed(9).slice(2)}$`,yt="?"+x,Bt=`<${yt}>`,E=document,I=()=>E.createComment(""),D=n=>n===null||typeof n!="object"&&typeof n!="function",rt=Array.isArray,Lt=n=>rt(n)||typeof n?.[Symbol.iterator]=="function",Y=`[ 	
\f\r]`,O=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,gt=/-->/g,ft=/>/g,w=RegExp(`>|${Y}(?:([^\\s"'>=/]+)(${Y}*=${Y}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),_t=/'/g,bt=/"/g,xt=/^(?:script|style|textarea|title)$/i,st=n=>(e,...t)=>({_$litType$:n,strings:e,values:t}),a=st(1),Xt=st(2),te=st(3),k=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),vt=new WeakMap,S=E.createTreeWalker(E,129);function wt(n,e){if(!rt(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return mt!==void 0?mt.createHTML(e):e}var jt=(n,e)=>{let t=n.length-1,i=[],r,s=e===2?"<svg>":e===3?"<math>":"",o=O;for(let l=0;l<t;l++){let c=n[l],h,p,u=-1,_=0;for(;_<c.length&&(o.lastIndex=_,p=o.exec(c),p!==null);)_=o.lastIndex,o===O?p[1]==="!--"?o=gt:p[1]!==void 0?o=ft:p[2]!==void 0?(xt.test(p[2])&&(r=RegExp("</"+p[2],"g")),o=w):p[3]!==void 0&&(o=w):o===w?p[0]===">"?(o=r??O,u=-1):p[1]===void 0?u=-2:(u=o.lastIndex-p[2].length,h=p[1],o=p[3]===void 0?w:p[3]==='"'?bt:_t):o===bt||o===_t?o=w:o===gt||o===ft?o=O:(o=w,r=void 0);let v=o===w&&n[l+1].startsWith("/>")?" ":"";s+=o===O?c+Bt:u>=0?(i.push(h),c.slice(0,u)+$t+c.slice(u)+x+v):c+x+(u===-2?l:v)}return[wt(n,s+(n[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),i]},U=class n{constructor({strings:e,_$litType$:t},i){let r;this.parts=[];let s=0,o=0,l=e.length-1,c=this.parts,[h,p]=jt(e,t);if(this.el=n.createElement(h,i),S.currentNode=this.el.content,t===2||t===3){let u=this.el.content.firstChild;u.replaceWith(...u.childNodes)}for(;(r=S.nextNode())!==null&&c.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let u of r.getAttributeNames())if(u.endsWith($t)){let _=p[o++],v=r.getAttribute(u).split(x),B=/([.?@])?(.*)/.exec(_);c.push({type:1,index:s,name:B[2],strings:v,ctor:B[1]==="."?Z:B[1]==="?"?X:B[1]==="@"?tt:R}),r.removeAttribute(u)}else u.startsWith(x)&&(c.push({type:6,index:s}),r.removeAttribute(u));if(xt.test(r.tagName)){let u=r.textContent.split(x),_=u.length-1;if(_>0){r.textContent=F?F.emptyScript:"";for(let v=0;v<_;v++)r.append(u[v],I()),S.nextNode(),c.push({type:2,index:++s});r.append(u[_],I())}}}else if(r.nodeType===8)if(r.data===yt)c.push({type:2,index:s});else{let u=-1;for(;(u=r.data.indexOf(x,u+1))!==-1;)c.push({type:7,index:s}),u+=x.length-1}s++}}static createElement(e,t){let i=E.createElement("template");return i.innerHTML=e,i}};function A(n,e,t=n,i){if(e===k)return e;let r=i!==void 0?t._$Co?.[i]:t._$Cl,s=D(e)?void 0:e._$litDirective$;return r?.constructor!==s&&(r?._$AO?.(!1),s===void 0?r=void 0:(r=new s(n),r._$AT(n,t,i)),i!==void 0?(t._$Co??=[])[i]=r:t._$Cl=r),r!==void 0&&(e=A(n,r._$AS(n,e.values),r,i)),e}var Q=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:i}=this._$AD,r=(e?.creationScope??E).importNode(t,!0);S.currentNode=r;let s=S.nextNode(),o=0,l=0,c=i[0];for(;c!==void 0;){if(o===c.index){let h;c.type===2?h=new z(s,s.nextSibling,this,e):c.type===1?h=new c.ctor(s,c.name,c.strings,this,e):c.type===6&&(h=new et(s,this,e)),this._$AV.push(h),c=i[++l]}o!==c?.index&&(s=S.nextNode(),o++)}return S.currentNode=E,r}p(e){let t=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}},z=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,r){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=A(this,e,t),D(e)?e===d||e==null||e===""?(this._$AH!==d&&this._$AR(),this._$AH=d):e!==this._$AH&&e!==k&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Lt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==d&&D(this._$AH)?this._$AA.nextSibling.data=e:this.T(E.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:i}=e,r=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=U.createElement(wt(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===r)this._$AH.p(t);else{let s=new Q(r,this),o=s.u(this.options);s.p(t),this.T(o),this._$AH=s}}_$AC(e){let t=vt.get(e.strings);return t===void 0&&vt.set(e.strings,t=new U(e)),t}k(e){rt(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,i,r=0;for(let s of e)r===t.length?t.push(i=new n(this.O(I()),this.O(I()),this,this.options)):i=t[r],i._$AI(s),r++;r<t.length&&(this._$AR(i&&i._$AB.nextSibling,r),t.length=r)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let i=ut(e).nextSibling;ut(e).remove(),e=i}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},R=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,r,s){this.type=1,this._$AH=d,this._$AN=void 0,this.element=e,this.name=t,this._$AM=r,this.options=s,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=d}_$AI(e,t=this,i,r){let s=this.strings,o=!1;if(s===void 0)e=A(this,e,t,0),o=!D(e)||e!==this._$AH&&e!==k,o&&(this._$AH=e);else{let l=e,c,h;for(e=s[0],c=0;c<s.length-1;c++)h=A(this,l[i+c],t,c),h===k&&(h=this._$AH[c]),o||=!D(h)||h!==this._$AH[c],h===d?e=d:e!==d&&(e+=(h??"")+s[c+1]),this._$AH[c]=h}o&&!r&&this.j(e)}j(e){e===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},Z=class extends R{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===d?void 0:e}},X=class extends R{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==d)}},tt=class extends R{constructor(e,t,i,r,s){super(e,t,i,r,s),this.type=5}_$AI(e,t=this){if((e=A(this,e,t,0)??d)===k)return;let i=this._$AH,r=e===d&&i!==d||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,s=e!==d&&(i===d||r);r&&this.element.removeEventListener(this.name,this,i),s&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},et=class{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){A(this,e)}};var qt=it.litHtmlPolyfillSupport;qt?.(U,z),(it.litHtmlVersions??=[]).push("3.3.3");var St=(n,e,t)=>{let i=t?.renderBefore??e,r=i._$litPart$;if(r===void 0){let s=t?.renderBefore??null;i._$litPart$=r=new z(e.insertBefore(I(),s),s,void 0,t??{})}return r._$AI(n),r};var nt=globalThis,$=class extends y{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=St(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return k}};$._$litElement$=!0,$.finalized=!0,nt.litElementHydrateSupport?.({LitElement:$});var Gt=nt.litElementPolyfillSupport;Gt?.({LitElement:$});(nt.litElementVersions??=[]).push("4.2.2");var Ft={attribute:!0,type:String,converter:H,reflect:!1,hasChanged:G},Wt=(n=Ft,e,t)=>{let{kind:i,metadata:r}=t,s=globalThis.litPropertyMetadata.get(r);if(s===void 0&&globalThis.litPropertyMetadata.set(r,s=new Map),i==="setter"&&((n=Object.create(n)).wrapped=!0),s.set(t.name,n),i==="accessor"){let{name:o}=t;return{set(l){let c=e.get.call(this);e.set.call(this,l),this.requestUpdate(o,c,n,!0,l)},init(l){return l!==void 0&&this.C(o,void 0,n,l),l}}}if(i==="setter"){let{name:o}=t;return function(l){let c=this[o];e.call(this,l),this.requestUpdate(o,c,n,!0,l)}}throw Error("Unsupported decorator location: "+i)};function C(n){return(e,t)=>typeof t=="object"?Wt(n,e,t):((i,r,s)=>{let o=r.hasOwnProperty(s);return r.constructor.createProperty(s,i),o?Object.getOwnPropertyDescriptor(r,s):void 0})(n,e,t)}function g(n){return C({...n,state:!0,attribute:!1})}function V(n,e){customElements.whenDefined("home-assistant").then(()=>{customElements.get(n)||customElements.define(n,e)})}function Et(n){window.customCards=window.customCards??[],window.customCards.some(e=>e.type===n.type)||window.customCards.push(n)}var kt={unavailable:{label:"Unavailable",tone:"bad"},hue_color_no_area:{label:"Not in an area",tone:"warn"},streamable:{label:"Effects",tone:"good"},rest_only:{label:"Home Assistant",tone:"neutral"}},At=[0,.5,1,2,3,5,10,20,30];function ot(n){return n<=0?"snap":n<1?`${n}s`:`${Number.isInteger(n)?n:n.toFixed(1)}s`}var at=(n,e,t,i,r)=>({key:n,label:e,type:"number",default:0,minimum:0,maximum:i,step:r,unit:t,options:[],help:""}),Vt=[{key:"targets",label:"Lights",type:"entities",default:[],minimum:null,maximum:null,step:null,unit:"",options:[],help:""},{...at("hold_ms","Hold","ms",6e4,10),default:500,minimum:50},at("fade_in","Fade in","s",10,.1),at("fade_out","Fade out","s",10,.1)],f=class extends ${constructor(){super(...arguments);this._effects=[];this._busy=!1;this._creatingShow=!1;this._newShowName="";this._importing=!1;this._addingEffect=!1;this._draftParams={};this._createShow=()=>{let t=this._newShowName.trim();t&&(this._run("lighting_console/shows/create",{name:t}),this._newShowName="",this._creatingShow=!1)};this._deleteShow=()=>{let t=this._show;if(!t)return;confirm(`Delete "${t.name}" and all ${t.cues.length} of its cues?

This cannot be undone.`)&&this._run("lighting_console/shows/delete",{show_id:t.id})};this._openImport=()=>{this._importing=!0,this._importGroups=void 0,(async()=>{try{let t=await this._call("lighting_console/import/groups");this._importGroups=t.groups}catch(t){this._error=t instanceof Error?t.message:String(t),this._importing=!1}})()};this._previewDraft=()=>{this._draftEffect&&(async()=>{try{await this._call("lighting_console/effects/preview",{effect:this._draftEffect,params:this._draftParams}),this._summary=await this._call("lighting_console/shows/list")}catch(t){this._error=t instanceof Error?t.message:String(t)}})()};this._saveDraft=()=>{this._draftEffect&&(this._run("lighting_console/cues/add_effect",{effect:this._draftEffect,params:this._draftParams}),this._addingEffect=!1,this._draftEffect=void 0)};this._snapshotShow=()=>{let t=this._show;if(!t)return;let i=new Date().toISOString().slice(0,16).replace("T"," ");this._run("lighting_console/shows/duplicate",{show_id:t.id,name:`${t.name} \u2014 snapshot ${i}`})}}updated(t){t.has("hass")&&this.hass&&!this._summary&&!this._error&&this._load()}async _call(t,i={}){return this.hass.callWS({type:t,...i})}async _load(){try{let[t,i,r]=await Promise.all([this._call("lighting_console/shows/list"),this._call("lighting_console/effects/list"),this._call("lighting_console/rig/list")]);this._summary=t,this._effects=i.effects,this._rig=r,this._error=void 0}catch(t){this._error=t instanceof Error?t.message:String(t)}}_run(t,i={}){this._busy||(this._busy=!0,(async()=>{try{this._summary=await this._call(t,i),this._error=void 0}catch(r){this._error=r instanceof Error?r.message:String(r)}finally{this._busy=!1}})())}get _show(){return this._summary?.active_show??null}get _cues(){return this._show?.cues??[]}render(){return this._error?a`<div class="error">
        <b>The console could not be reached.</b>
        <div>${this._error}</div>
        <button @click=${()=>{this._error=void 0,this._load()}}>
          Try again
        </button>
      </div>`:this._summary?a`
      ${this._renderShowBar()}
      ${this._show?this._renderConsole():this._renderNoShow()}
    `:a`<div class="muted">Loading…</div>`}_renderNoShow(){return a`
      <div class="empty">
        <h3>No show yet</h3>
        <p>
          A show is one production and its cue list. Name it after the thing
          you are lighting — <i>Carrie</i>, <i>Company</i> — and start
          recording cues into it.
        </p>
        <button class="primary big" @click=${()=>this._creatingShow=!0}>
          Create a show
        </button>
      </div>
    `}_renderShowBar(){let t=this._summary;return a`
      <div class="showbar">
        <select
          .value=${t.active_show_id??""}
          ?disabled=${this._busy||t.shows.length===0}
          @change=${i=>this._run("lighting_console/shows/activate",{show_id:i.target.value})}
        >
          ${t.shows.map(i=>a`<option value=${i.id}>
              ${i.name} · ${i.cue_count} cue${i.cue_count===1?"":"s"}
            </option>`)}
        </select>
        <button @click=${()=>this._creatingShow=!0}>New show</button>
        <button @click=${this._openImport}>Import from Hue</button>
        ${this._show?a`<button
                @click=${this._snapshotShow}
                title="Copy this show, cues and all, as a snapshot to fall back to"
              >
                Snapshot
              </button>
              <button
                class="danger-text"
                @click=${this._deleteShow}
                title="Delete this show and every cue in it"
              >
                Delete show
              </button>`:d}
      </div>
      ${this._creatingShow?this._renderCreateShow():d}
      ${this._importing?this._renderImport():d}
    `}_renderCreateShow(){return a`
      <div class="panel">
        <label>
          Show name
          <input
            autofocus
            placeholder="Carrie"
            .value=${this._newShowName}
            @input=${t=>this._newShowName=t.target.value}
            @keydown=${t=>{t.key==="Enter"&&this._createShow(),t.key==="Escape"&&(this._creatingShow=!1)}}
          />
        </label>
        <div class="row">
          <button
            class="primary"
            ?disabled=${!this._newShowName.trim()}
            @click=${this._createShow}
          >
            Create
          </button>
          <button @click=${()=>this._creatingShow=!1}>Cancel</button>
        </div>
      </div>
    `}_renderImport(){return a`
      <div class="panel">
        <h4>Import a show from the Hue bridge</h4>
        <p class="muted">
          Each Hue room or zone that holds scenes becomes a show, one cue per
          scene, in cue-number order. The cues are copied — editing them here
          does not touch the bridge.
        </p>
        ${this._importGroups===void 0?a`<div class="muted">Reading the bridge…</div>`:this._importGroups.length===0?a`<div class="muted">No rooms or zones on the bridge have scenes.</div>`:a`<div class="grouplist">
                ${this._importGroups.map(t=>a`
                    <button
                      class=${t.importable?"grouprow":"grouprow dead"}
                      ?disabled=${this._busy||!t.importable}
                      title=${t.reason}
                      @click=${()=>this._runImport(t)}
                    >
                      <span class="glabel">${t.name}</span>
                      <span class="muted"
                        >${t.type} · ${t.scene_count} scenes ·
                        ${t.light_count} lights</span
                      >
                      ${t.reason?a`<span
                            class=${t.importable?"note":"note bad"}
                            >${t.reason}</span
                          >`:d}
                    </button>
                  `)}
              </div>`}
        <div class="row">
          <button @click=${()=>this._importing=!1}>Close</button>
        </div>
      </div>
    `}_runImport(t){this._run("lighting_console/import/run",{group_id:t.id,name:t.name,default_fade:0}),this._importing=!1}_renderConsole(){let t=this._summary.playback,i=this._cues,r=t.current_index===null?null:i[t.current_index]??null,s=t.current_index===null?i[0]:i[t.current_index+1];return a`
      <div class="transport">
        <button
          class="go"
          ?disabled=${this._busy||!s}
          @click=${()=>this._run("lighting_console/playback/go")}
        >
          <span class="golabel">GO</span>
          <span class="gonext">${s?s.label:"end of show"}</span>
        </button>
        <div class="transport-side">
          <button
            ?disabled=${this._busy||t.current_index===null||t.current_index<=0}
            @click=${()=>this._run("lighting_console/playback/back")}
          >
            Back
          </button>
          <button
            class="danger"
            @click=${()=>this._run("lighting_console/playback/release")}
            title="Stop every effect and take the rig to black"
          >
            Release
          </button>
        </div>
      </div>

      <div class="statusline">
        <span
          >On stage:
          <b>${r?`${r.label}${r.name?` \u2014 ${r.name}`:""}`:"nothing"}</b></span
        >
        ${t.effect.running?a`<span class="running"
              >${t.effect.running} running
              <button @click=${()=>this._stopEffect()}>Stop</button></span
            >`:d}
      </div>

      <div class="recordbar">
        <button
          class="record"
          ?disabled=${this._busy}
          @click=${()=>this._run("lighting_console/cues/record")}
          title="Capture what the lights are doing right now as a new cue"
        >
          ● Record cue
        </button>
        <button ?disabled=${this._busy} @click=${()=>this._addingEffect=!0}>
          + Effect cue
        </button>
      </div>

      ${this._addingEffect?this._renderEffectDraft():d}
      ${i.length===0?this._renderNoCues():this._renderCues(i,t.current_cue_id)}
    `}_renderNoCues(){return a`
      <div class="empty">
        <h3>No cues yet</h3>
        <p>
          Set the lights however you want them — using the normal Home
          Assistant light controls, the Hue app, anything — then press
          <b>Record cue</b>. The console stores exactly what the rig is doing,
          including the lights that are off.
        </p>
      </div>
    `}_renderCues(t,i){return a`
      <table class="cues">
        <thead>
          <tr>
            <th class="c-label">Cue</th>
            <th>Name</th>
            <th class="c-fade">Fade</th>
            <th class="c-actions"></th>
          </tr>
        </thead>
        <tbody>
          ${t.map((r,s)=>this._renderCueRow(r,s,i))}
        </tbody>
      </table>
    `}_renderCueRow(t,i,r){let s=t.id===r,o=t.id===this._editingCueId;return a`
      <tr
        class=${`cue ${s?"live":""} ${o?"editing":""}`}
        draggable="true"
        @dragstart=${()=>this._dragFrom=i}
        @dragover=${l=>l.preventDefault()}
        @drop=${()=>this._dropOn(i)}
      >
        <td class="c-label">
          <button
            class="labelbtn"
            title="Go to this cue"
            ?disabled=${this._busy}
            @click=${()=>this._run("lighting_console/playback/goto",{cue_id:t.id})}
          >
            ${t.label}
          </button>
        </td>
        <td>
          ${t.kind==="effect"?a`<span class="badge">${t.effect}</span> `:d}${t.name||a`<span class="muted">—</span>`}
        </td>
        <td class="c-fade">${t.kind==="effect"?"\u2014":ot(t.fade)}</td>
        <td class="c-actions">
          <button title="Move up" ?disabled=${i===0} @click=${()=>this._move(i,-1)}>↑</button>
          <button title="Move down" ?disabled=${i===this._cues.length-1} @click=${()=>this._move(i,1)}>↓</button>
          <button title="Edit" @click=${()=>this._editingCueId=o?void 0:t.id}>Edit</button>
        </td>
      </tr>
      ${o?a`<tr class="editorrow"><td colspan="4">${this._renderCueEditor(t,i)}</td></tr>`:d}
    `}_renderCueEditor(t,i){return a`
      <div class="editor">
        <div class="row">
          <label class="grow">
            Cue number
            <input
              .value=${t.label}
              @change=${r=>this._update(t.id,{label:r.target.value})}
            />
          </label>
          <label class="grow2">
            Name
            <input
              .value=${t.name}
              placeholder="what this cue is for"
              @change=${r=>this._update(t.id,{name:r.target.value})}
            />
          </label>
        </div>

        ${t.kind==="look"?a`
              <div class="row wrap">
                <span class="fadelabel">Fade</span>
                ${At.map(r=>a`<button
                    class=${t.fade===r?"chip on":"chip"}
                    @click=${()=>this._update(t.id,{fade:r})}
                  >
                    ${ot(r)}
                  </button>`)}
                <input
                  class="fadeinput"
                  type="number"
                  min="0"
                  step="0.05"
                  .value=${String(t.fade)}
                  @change=${r=>this._update(t.id,{fade:Number(r.target.value)})}
                />
              </div>
              <div class="row">
                <button
                  @click=${()=>this._run("lighting_console/cues/rerecord",{cue_id:t.id})}
                  title="Replace this cue's look with what the lights are doing now"
                >
                  Re-record from the live rig
                </button>
                <span class="muted"
                  >${t.levels.filter(r=>r.state==="on").length} of
                  ${t.levels.length} lights on</span
                >
              </div>
            `:this._renderEffectParams(t.effect??"",t.effect_params,r=>this._update(t.id,{effect_params:r}))}

        ${t.notes?a`<div class="muted notes">${t.notes}</div>`:d}

        <div class="row">
          <button @click=${()=>this._insertAfter(i)}>
            Insert a cue after this one
          </button>
          <button @click=${()=>this._duplicateCue(t)}>Duplicate ${t.label}</button>
          <button class="danger-text" @click=${()=>this._deleteCue(t)}>
            Delete ${t.label}
          </button>
        </div>
      </div>
    `}_renderEffectDraft(){let t=this._effects.find(i=>i.name===this._draftEffect);return a`
      <div class="panel">
        <h4>Effect cue</h4>
        <div class="row wrap">
          ${this._effects.map(i=>a`<button
              class=${i.name===this._draftEffect?"chip on":"chip"}
              @click=${()=>{this._draftEffect=i.name,this._draftParams=Object.fromEntries(i.params.map(r=>[r.key,r.default]))}}
            >
              ${i.label}
            </button>`)}
        </div>
        ${t?a`
              <p class="muted">${t.description}</p>
              ${this._renderEffectParams(t.name,this._draftParams,i=>{this._draftParams=i})}
              <div class="row">
                <button @click=${this._previewDraft}>Try it</button>
                <button @click=${()=>this._stopEffect()}>Stop</button>
                <button class="primary" @click=${this._saveDraft}>
                  Save as a cue
                </button>
                <button @click=${()=>this._addingEffect=!1}>Cancel</button>
              </div>
            `:a`<div class="row">
              <button @click=${()=>this._addingEffect=!1}>Cancel</button>
            </div>`}
      </div>
    `}_renderEffectParams(t,i,r){let s=this._effects.find(l=>l.name===t);if(!s)return a`<div class="muted">Unknown effect.</div>`;let o=(l,c)=>r({...i,[l]:c});return a`
      <div class="params">
        ${s.params.map(l=>this._renderParam(l,i,o))}
      </div>
    `}_renderParam(t,i,r){let s=i[t.key]??t.default;if(t.type==="number")return a`<label>
        ${t.label}${t.unit?` (${t.unit})`:""}
        <input
          type="number"
          .value=${String(s??"")}
          min=${t.minimum??d}
          max=${t.maximum??d}
          step=${t.step??d}
          @change=${o=>r(t.key,Number(o.target.value))}
        />
        ${t.help?a`<small class="muted">${t.help}</small>`:d}
      </label>`;if(t.type==="select")return a`<label>
        ${t.label}
        <select
          .value=${String(s??"")}
          @change=${o=>r(t.key,o.target.value)}
        >
          ${t.options.map(o=>a`<option value=${o}>${o}</option>`)}
        </select>
      </label>`;if(t.type==="color"){let o=s??[[255,255,255]];return a`<label>
        ${t.label}
        <span class="colors">
          ${o.map((l,c)=>a`<input
              type="color"
              .value=${T(l)}
              @change=${h=>{let p=o.map((u,_)=>_===c?Rt(h.target.value):u);r(t.key,p)}}
            />`)}
          <button
            class="chip"
            title="Add another colour to cycle through"
            @click=${()=>r(t.key,[...o,[255,255,255]])}
          >
            +
          </button>
          ${o.length>1?a`<button class="chip" @click=${()=>r(t.key,o.slice(0,-1))}>
                −
              </button>`:d}
        </span>
        ${this._renderSwatches(o,l=>r(t.key,l))}
        ${t.help?a`<small class="muted">${t.help}</small>`:d}
      </label>`}if(t.type==="entities"){let o=(s??[]).filter(h=>typeof h=="string"),l=this._rig?.members??[],c=h=>r(t.key,o.includes(h)?o.filter(p=>p!==h):[...o,h]);return a`<label class="wide">
        ${t.label}
        <span class="targets">
          ${l.length===0?a`<small class="muted"
                >No lights in the rig yet — add them on the Rig tab.</small
              >`:l.map(h=>{let p=o.indexOf(h.entity_id);return a`<button
                  class=${p>=0?"chip on":"chip"}
                  title=${h.entity_id}
                  @click=${()=>c(h.entity_id)}
                >
                  ${p>=0?a`<span class="ord">${p+1}</span>`:d}${h.name}
                </button>`})}
        </span>
        <span class="targets">
          <button class="chip" @click=${()=>r(t.key,[])}>
            Whole rig
          </button>
          <button
            class="chip"
            @click=${()=>r(t.key,l.map(h=>h.entity_id))}
          >
            All, in rig order
          </button>
          ${o.length>1?a`<button
                class="chip"
                title="Walk them the other way"
                @click=${()=>r(t.key,[...o].reverse())}
              >
                Reverse
              </button>`:d}
        </span>
        <small class="muted">
          ${o.length===0?"Empty means the whole rig, in rig order.":`${o.length} light${o.length===1?"":"s"}, driven in the order shown.`}
        </small>
      </label>`}if(t.type==="steps"){let o=s??[],l=(h,p)=>r(t.key,o.map((u,_)=>_===h?p:u)),c={targets:[],color:[255,255,255],hold_ms:500,fade_in:0,fade_out:0};return a`<div class="wide steps">
        ${t.label}
        ${o.map((h,p)=>a`<div class="step">
            <div class="step-head">
              <span class="ord">${p+1}</span>
              <input
                type="color"
                .value=${T(h.color)}
                @change=${u=>l(p,{...h,color:Rt(u.target.value)})}
              />
              ${this._renderSwatches([h.color],u=>l(p,{...h,color:u[u.length-1]}))}
              <button
                class="chip"
                title="Remove this step"
                ?disabled=${o.length<=1}
                @click=${()=>r(t.key,o.filter((u,_)=>_!==p))}
              >
                −
              </button>
            </div>
            <div class="params">
              ${Vt.map(u=>this._renderParam(u,h,(_,v)=>l(p,{...h,[_]:v})))}
            </div>
          </div>`)}
        <button class="chip" @click=${()=>r(t.key,[...o,c])}>
          + Add a step
        </button>
        ${t.help?a`<small class="muted">${t.help}</small>`:d}
      </div>`}return a`<label>
      ${t.label}
      <input
        type="checkbox"
        .checked=${!!s}
        @change=${o=>r(t.key,o.target.checked)}
      />
    </label>`}_stopEffect(){(async()=>{try{await this._call("lighting_console/effects/stop"),this._summary=await this._call("lighting_console/shows/list")}catch(t){this._error=t instanceof Error?t.message:String(t)}})()}_update(t,i){this._run("lighting_console/cues/update",{cue_id:t,changes:i})}_deleteCue(t){confirm(`Delete ${t.label}?`)&&(this._editingCueId=void 0,this._run("lighting_console/cues/delete",{cue_id:t.id}))}_renderSwatches(t,i){let r=this._show;if(!r)return a``;let s=r.colors??[],o=t[t.length-1],l=p=>i([...t.slice(0,-1),p]),c=()=>this._run("lighting_console/shows/rename",{show_id:r.id,colors:[...s,o]}),h=s.some(p=>T(p)===T(o));return a`<span class="colors swatches">
      ${s.map(p=>a`<button
          class="swatch"
          style="background:${T(p)}"
          title="Use ${T(p)}"
          @click=${()=>l(p)}
        ></button>`)}
      ${h?d:a`<button class="chip" title="Save this colour to the show" @click=${c}>
            ★ save
          </button>`}
    </span>`}_duplicateCue(t){this._run("lighting_console/cues/duplicate",{cue_id:t.id})}_insertAfter(t){this._run("lighting_console/cues/record",{at:t+1})}_move(t,i){let r=this._cues.map(o=>o.id),s=t+i;s<0||s>=r.length||([r[t],r[s]]=[r[s],r[t]],this._run("lighting_console/cues/reorder",{cue_ids:r}))}_dropOn(t){let i=this._dragFrom;if(this._dragFrom=void 0,i===void 0||i===t)return;let r=this._cues.map(o=>o.id),[s]=r.splice(i,1);r.splice(t,0,s),this._run("lighting_console/cues/reorder",{cue_ids:r})}};f.styles=M`
    :host {
      display: block;
    }
    .muted {
      color: var(--secondary-text-color);
      font-size: 0.85em;
    }
    .row {
      display: flex;
      gap: 8px;
      align-items: flex-end;
      margin-top: 8px;
    }
    .row.wrap {
      flex-wrap: wrap;
      align-items: center;
    }
    .grow {
      flex: 1;
    }
    .grow2 {
      flex: 2;
    }
    label {
      display: flex;
      flex-direction: column;
      gap: 2px;
      font-size: 0.8em;
      color: var(--secondary-text-color);
    }
    input,
    select {
      padding: 6px 8px;
      border-radius: 6px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color);
      color: var(--primary-text-color);
      font-size: 1rem;
      font: inherit;
    }
    button {
      padding: 6px 10px;
      border-radius: 6px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color);
      color: var(--primary-text-color);
      cursor: pointer;
      font: inherit;
    }
    button:disabled {
      opacity: 0.4;
      cursor: default;
    }
    button.primary {
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      border-color: transparent;
    }
    button.big {
      padding: 12px 20px;
      font-size: 1.1em;
    }
    button.danger {
      border-color: var(--error-color, #db4437);
      color: var(--error-color, #db4437);
    }
    button.danger-text {
      color: var(--error-color, #db4437);
      border-color: transparent;
    }
    .error {
      padding: 12px;
      border-radius: 8px;
      background: rgba(219, 68, 55, 0.1);
      border: 1px solid var(--error-color, #db4437);
    }
    .empty {
      text-align: center;
      padding: 24px 12px;
    }
    .empty h3 {
      margin: 0 0 4px;
    }
    .empty p {
      color: var(--secondary-text-color);
      max-width: 46ch;
      margin: 0 auto 12px;
      font-size: 0.9em;
    }

    .showbar {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
      margin-bottom: 12px;
    }
    .showbar select {
      flex: 1;
      min-width: 12ch;
    }

    .panel {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 12px;
    }
    .panel h4 {
      margin: 0 0 4px;
    }

    /* Transport. GO is deliberately the largest thing on the card. */
    .transport {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
    }
    .go {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      padding: 18px;
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      border: none;
      border-radius: 10px;
    }
    .golabel {
      font-size: 1.8em;
      font-weight: 700;
      line-height: 1;
      letter-spacing: 0.05em;
    }
    .gonext {
      font-size: 0.8em;
      opacity: 0.85;
    }
    .transport-side {
      display: flex;
      flex-direction: column;
      gap: 8px;
      justify-content: stretch;
      min-width: 96px;
    }
    .transport-side button {
      flex: 1;
    }

    /* A touch screen — the iPad the show is run from. Laptops keep the
       denser layout; here every target the operator hits in the dark is a
       fingertip wide, and GO/Back/Release most of all. */
    @media (pointer: coarse) {
      .go {
        padding: 30px 18px;
      }
      .golabel {
        font-size: 2.4em;
      }
      .gonext {
        font-size: 1em;
      }
      .transport {
        gap: 12px;
      }
      .transport-side {
        gap: 12px;
        min-width: 132px;
      }
      .transport-side button {
        min-height: 60px;
        font-size: 1.1em;
      }
      .record {
        padding: 18px;
      }
      tr.cue td {
        padding: 6px 6px;
      }
      .labelbtn,
      .c-actions button {
        min-height: 44px;
      }
      .c-actions button {
        min-width: 44px;
      }
      .chip {
        min-height: 36px;
        padding: 6px 12px;
      }
      .colors input[type="color"] {
        width: 52px;
        height: 44px;
      }
      .swatch {
        width: 40px;
        height: 40px;
      }
      button,
      input,
      select {
        min-height: 40px;
      }
      input[type="checkbox"] {
        min-height: 0;
        width: 24px;
        height: 24px;
      }
    }

    .statusline {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
      font-size: 0.85em;
      color: var(--secondary-text-color);
      margin-bottom: 12px;
    }
    .running {
      color: var(--warning-color, #ffa600);
      display: flex;
      gap: 6px;
      align-items: center;
    }

    .recordbar {
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
    }
    .record {
      flex: 1;
      padding: 14px;
      font-size: 1.05em;
      font-weight: 600;
      border-color: var(--error-color, #db4437);
      color: var(--error-color, #db4437);
    }

    table.cues {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95em;
    }
    table.cues th {
      text-align: left;
      font-size: 0.75em;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--secondary-text-color);
      border-bottom: 1px solid var(--divider-color);
      padding: 4px 6px;
    }
    tr.cue td {
      padding: 4px 6px;
      border-bottom: 1px solid var(--divider-color);
      vertical-align: middle;
    }
    tr.cue.live {
      background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.14);
    }
    tr.cue.live .labelbtn {
      font-weight: 700;
    }
    .c-label {
      /* Shrink to the widest label, never wrap it: "Start Queue preset" on
         three lines pushed every row apart and hid the running order. */
      width: 1%;
      white-space: nowrap;
    }
    .c-fade {
      width: 6ch;
      text-align: right;
      color: var(--secondary-text-color);
    }
    .c-actions {
      width: 1%;
      white-space: nowrap;
      text-align: right;
    }
    .c-actions button {
      padding: 2px 8px;
      min-height: 32px;
      min-width: 32px;
      font-size: 0.9em;
    }
    .labelbtn {
      border: none;
      background: none;
      padding: 2px 4px;
      font-weight: 600;
      color: var(--primary-text-color);
      max-width: 22ch;
      overflow: hidden;
      text-overflow: ellipsis;
      font-variant-numeric: tabular-nums;
      min-height: 32px;
    }
    .badge {
      display: inline-block;
      padding: 1px 6px;
      border-radius: 999px;
      font-size: 0.75em;
      background: var(--secondary-background-color);
      color: var(--secondary-text-color);
      margin-right: 4px;
    }
    .editorrow td {
      padding: 0 6px 12px;
      border-bottom: 1px solid var(--divider-color);
    }
    .editor {
      border-left: 3px solid var(--primary-color);
      padding: 8px 12px;
      background: var(--secondary-background-color);
      border-radius: 0 8px 8px 0;
    }
    .fadelabel {
      font-size: 0.8em;
      color: var(--secondary-text-color);
    }
    .fadeinput {
      width: 8ch;
    }
    .chip {
      padding: 4px 10px;
      min-height: 30px;
      border-radius: 999px;
      font-size: 0.85em;
    }
    .chip.on {
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      border-color: transparent;
    }
    .params {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
      margin-top: 8px;
    }
    .colors {
      display: flex;
      gap: 4px;
      align-items: center;
    }
    label.wide,
    .wide {
      grid-column: 1 / -1;
    }
    .step {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      padding: 8px;
      margin-top: 8px;
    }
    .step-head {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .steps > small {
      display: block;
      margin-top: 6px;
    }
    .targets {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin: 2px 0;
    }
    .ord {
      display: inline-block;
      min-width: 1.4em;
      margin-right: 4px;
      padding: 0 4px;
      border-radius: 999px;
      background: rgba(0, 0, 0, 0.25);
      font-size: 0.85em;
      font-variant-numeric: tabular-nums;
    }
    .colors {
      flex-wrap: wrap;
    }
    .colors input[type="color"] {
      width: 44px;
      height: 36px;
      padding: 2px;
    }
    .swatch {
      width: 32px;
      height: 32px;
      padding: 0;
      border-radius: 6px;
      border: 1px solid rgba(0, 0, 0, 0.3);
    }
    .notes {
      margin-top: 8px;
      font-style: italic;
    }
    .grouplist {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-top: 8px;
    }
    .grouprow {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: baseline;
      text-align: left;
    }
    .glabel {
      font-weight: 600;
    }
    .grouprow {
      flex-wrap: wrap;
    }
    .grouprow.dead {
      opacity: 0.55;
    }
    .note {
      flex-basis: 100%;
      font-size: 0.8em;
      color: var(--secondary-text-color);
      text-align: left;
    }
    .note.bad {
      color: var(--warning-color, #ffa600);
    }
  `,m([C({attribute:!1})],f.prototype,"hass",2),m([g()],f.prototype,"_summary",2),m([g()],f.prototype,"_effects",2),m([g()],f.prototype,"_rig",2),m([g()],f.prototype,"_error",2),m([g()],f.prototype,"_busy",2),m([g()],f.prototype,"_creatingShow",2),m([g()],f.prototype,"_newShowName",2),m([g()],f.prototype,"_importing",2),m([g()],f.prototype,"_importGroups",2),m([g()],f.prototype,"_editingCueId",2),m([g()],f.prototype,"_addingEffect",2),m([g()],f.prototype,"_draftEffect",2),m([g()],f.prototype,"_draftParams",2),m([g()],f.prototype,"_dragFrom",2);function T(n){let[e,t,i]=n;return`#${[e,t,i].map(r=>Math.max(0,Math.min(255,r)).toString(16).padStart(2,"0")).join("")}`}function Rt(n){let e=n.replace("#","");return[parseInt(e.slice(0,2),16),parseInt(e.slice(2,4),16),parseInt(e.slice(4,6),16)]}V("lighting-console-cues",f);var Ct="lighting-console-card",b=class extends ${constructor(){super(...arguments);this._busy=!1;this._adding=!1;this._filter="";this._tab="show"}setConfig(t){this._config=t}getCardSize(){return 12}updated(t){t.has("hass")&&this.hass&&!this._info&&!this._error&&this._load()}async _call(t,i={}){return this.hass.callWS({type:t,...i})}async _load(){try{let[t,i,r]=await Promise.all([this._call("lighting_console/info"),this._call("lighting_console/rig/list"),this._call("lighting_console/bridge/status")]);this._info=t,this._rig=i,this._bridge=r,this._error=void 0}catch(t){this._error=t instanceof Error?t.message:String(t)}}async _withBusy(t){this._busy=!0;try{await t(),this._error=void 0}catch(i){this._error=i instanceof Error?i.message:String(i)}finally{this._busy=!1}}_refreshBridge(){this._withBusy(async()=>{let t=await this._call("lighting_console/bridge/refresh");this._bridge=t,this._rig=t.rig})}_moveMember(t,i){let r=(this._rig?.members??[]).map(o=>o.entity_id),s=t+i;s<0||s>=r.length||([r[t],r[s]]=[r[s],r[t]],this._withBusy(async()=>{this._rig=await this._call("lighting_console/rig/reorder",{entity_ids:r})}))}_remove(t){this._withBusy(async()=>{this._rig=await this._call("lighting_console/rig/remove",{entity_ids:[t]})})}_add(t){this._withBusy(async()=>{this._rig=await this._call("lighting_console/rig/add",{entity_ids:[t]}),this._candidates=this._candidates?.filter(i=>i.entity_id!==t)})}_openAdd(){this._adding=!0,this._withBusy(async()=>{let t=await this._call("lighting_console/rig/candidates");this._candidates=t.candidates})}render(){return!this._config||!this.hass?d:a`
      <ha-card>
        <div class="header">
          <h1>${this._config.title??"Lighting Console"}</h1>
          ${this._renderBridgeChip()}
        </div>
        ${this._renderTabs()}
        <div class="content">
          ${this._error?this._renderError():this._renderBody()}
        </div>
        <div class="footer">${this._renderBuildStamp()}</div>
      </ha-card>
    `}_renderError(){return a`
      <div class="alert">
        <p><strong>Cannot reach the Lighting Console integration.</strong></p>
        <p class="detail">${this._error}</p>
        <p class="detail">
          Check that the integration is installed and set up under Settings →
          Devices &amp; services.
        </p>
      </div>
    `}_renderTabs(){let t=(i,r,s)=>a`
      <button
        class=${this._tab===i?"tab on":"tab"}
        title=${s}
        @click=${()=>this._tab=i}
      >
        ${r}
      </button>
    `;return a`
      <div class="tabs">
        ${t("show","Show","The cue list, GO, and recording")}
        ${t("rig","Rig","Which entities the console drives")}
      </div>
    `}_renderBody(){return this._tab==="show"?a`<lighting-console-cues
        .hass=${this.hass}
      ></lighting-console-cues>`:this._rig?a`
      ${this._renderBridge()} ${this._renderRig()}
      ${this._adding?this._renderCandidates():d}
    `:a`<p class="detail">Loading…</p>`}_renderBridgeChip(){return this._bridge?this._bridge.configured?this._bridge.reachable?this._bridge.has_client_key?a`<span class="chip good">Bridge ready</span>`:a`<span class="chip bad">No streaming key</span>`:a`<span class="chip bad">Bridge unreachable</span>`:a`<span class="chip warn">No bridge</span>`:d}_renderBridge(){let t=this._bridge;return t?t.configured?a`
      <section>
        <div class="section-head">
          <h2>Hue bridge</h2>
          <button
            class="link"
            ?disabled=${this._busy}
            @click=${this._refreshBridge}
          >
            Re-read bridge
          </button>
        </div>

        ${t.error?a`<p class="detail bad-text">${t.error}</p>`:a`<p class="detail">
              ${t.name??"Bridge"} · ${t.light_count} lights
            </p>`}
        ${t.has_client_key?d:a`<p class="detail bad-text">
              The console has no client key, so effects could never stream.
              Pair with the bridge again from Settings.
            </p>`}

        <h3>Entertainment areas</h3>
        ${t.entertainment_areas.length===0?a`<p class="detail">
              No entertainment areas exist on this bridge. Create one in the
              Hue app and add your colour lights to it, then choose "Re-read
              bridge" — until then no effect can run.
            </p>`:a`
              <ul class="areas">
                ${t.entertainment_areas.map(i=>a`
                    <li>
                      <span class="area-name">${i.name}</span>
                      <span class="detail">
                        ${i.light_count}
                        ${i.light_count===1?"light":"lights"} ·
                        ${i.channel_count}
                        ${i.channel_count===1?"channel":"channels"}
                      </span>
                      ${i.streaming?a`<span class="chip good">streaming</span>`:d}
                    </li>
                  `)}
              </ul>
            `}
      </section>
    `:a`
        <section>
          <h2>Hue bridge</h2>
          <p class="detail">
            No bridge is paired. The console works without one — every light is
            driven through Home Assistant — but effects need a bridge. To pair,
            go to Settings → Devices &amp; services → Lighting Console →
            Reconfigure.
          </p>
        </section>
      `:a``}_renderRig(){let t=this._rig;return a`
      <section>
        <div class="section-head">
          <h2>The rig (${t.total})</h2>
          <button class="link" ?disabled=${this._busy} @click=${this._openAdd}>
            Add lights
          </button>
        </div>

        ${t.total===0?a`<p class="detail">
              The rig is empty. Add the lights, plugs and switches this show
              uses — cues will capture every one of them automatically.
            </p>`:a`
              <ul class="rig">
                ${t.members.map((i,r)=>this._renderMember(i,r,t.members.length))}
              </ul>
            `}
      </section>
    `}_renderMember(t,i,r){let s=kt[t.capability];return a`
      <li>
        <div class="member">
          <span class="member-name">${t.name}</span>
          <span class="entity-id">${t.entity_id}</span>
          <span class="detail">${t.reason}</span>
        </div>
        <span class="chip ${s.tone}">${s.label}</span>
        <button
          class="link"
          title="Move up"
          ?disabled=${this._busy||i===0}
          @click=${()=>this._moveMember(i,-1)}
        >
          ↑
        </button>
        <button
          class="link"
          title="Move down"
          ?disabled=${this._busy||i===r-1}
          @click=${()=>this._moveMember(i,1)}
        >
          ↓
        </button>
        <button
          class="link danger"
          ?disabled=${this._busy}
          title="Remove from the rig"
          @click=${()=>this._remove(t.entity_id)}
        >
          Remove
        </button>
      </li>
    `}_renderCandidates(){let t=this._filter.trim().toLowerCase(),i=(this._candidates??[]).filter(r=>!t||r.name.toLowerCase().includes(t)||r.entity_id.toLowerCase().includes(t));return a`
      <section class="picker">
        <div class="section-head">
          <h2>Add to the rig</h2>
          <button class="link" @click=${()=>this._adding=!1}>
            Done
          </button>
        </div>
        <input
          type="search"
          placeholder="Filter lights and switches…"
          .value=${this._filter}
          @input=${r=>{this._filter=r.target.value}}
        />
        ${i.length===0?a`<p class="detail">Nothing left to add.</p>`:a`
              <ul class="rig">
                ${i.map(r=>a`
                    <li>
                      <div class="member">
                        <span class="member-name">${r.name}</span>
                        <span class="entity-id">${r.entity_id}</span>
                      </div>
                      <button
                        class="link"
                        ?disabled=${this._busy}
                        @click=${()=>this._add(r.entity_id)}
                      >
                        Add
                      </button>
                    </li>
                  `)}
              </ul>
            `}
      </section>
    `}_renderBuildStamp(){let t=this._info?`${this._info.version} \xB7 ${this._info.git_sha}`:"\u2014",i="0.5.0 \xB7 4bda023d226d",r=this._info!==void 0&&this._info.version!=="0.5.0",s=this._bridge?.configured?this._bridge.scene_error?a`<span class="warn-text" title=${this._bridge.scene_error}>
            scenes: ${this._bridge.scene_error}
          </span>`:a`<span class="stamp">${this._bridge.scene_count} scenes</span>`:d;return a`
      ${s}
      <span class="stamp ${r?"mismatch":""}">
        card ${i} / backend ${t}
      </span>
      ${r?a`<span class="warn-text" title="Card and integration versions differ">
            version mismatch
          </span>`:d}
    `}};b.styles=M`
    .tabs {
      display: flex;
      gap: 4px;
      padding: 0 16px;
      border-bottom: 1px solid var(--divider-color);
    }
    .tab {
      padding: 8px 14px;
      border: none;
      background: none;
      color: var(--secondary-text-color);
      cursor: pointer;
      font: inherit;
      font-weight: 500;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
    }
    .tab.on {
      color: var(--primary-color);
      border-bottom-color: var(--primary-color);
    }

    ha-card {
      display: flex;
      flex-direction: column;
      height: 100%;
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 16px 16px 0;
    }
    h1 {
      margin: 0;
      font-size: 1.4rem;
      font-weight: 500;
    }
    h2 {
      margin: 0;
      font-size: 1.05rem;
      font-weight: 500;
    }
    h3 {
      margin: 16px 0 4px;
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--secondary-text-color);
    }
    .content {
      flex: 1;
      padding: 8px 16px 16px;
    }
    section {
      padding: 12px 0;
      border-top: 1px solid var(--divider-color);
    }
    section:first-child {
      border-top: none;
    }
    .section-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .detail {
      color: var(--secondary-text-color);
      font-size: 0.9rem;
      margin: 4px 0;
    }
    .bad-text {
      color: var(--error-color, #db4437);
    }
    .warn-text {
      color: var(--warning-color, #ffa600);
      font-size: 0.75rem;
      font-weight: 500;
    }
    .alert {
      border-left: 4px solid var(--error-color, #db4437);
      padding-left: 12px;
    }
    ul {
      list-style: none;
      margin: 8px 0 0;
      padding: 0;
    }
    .rig li,
    .areas li {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 0;
      border-bottom: 1px solid var(--divider-color);
    }
    .rig li:last-child,
    .areas li:last-child {
      border-bottom: none;
    }
    .member {
      display: flex;
      flex-direction: column;
      flex: 1;
      min-width: 0;
    }
    .member-name,
    .area-name {
      font-weight: 500;
    }
    .entity-id {
      font-family: var(--code-font-family, monospace);
      font-size: 0.75rem;
      color: var(--secondary-text-color);
    }
    .chip {
      flex: none;
      border-radius: 12px;
      padding: 2px 10px;
      font-size: 0.75rem;
      font-weight: 500;
      white-space: nowrap;
      background: var(--secondary-background-color);
      color: var(--secondary-text-color);
    }
    .chip.good {
      background: color-mix(in srgb, var(--success-color, #43a047) 18%, transparent);
      color: var(--success-color, #43a047);
    }
    .chip.warn {
      background: color-mix(in srgb, var(--warning-color, #ffa600) 20%, transparent);
      color: var(--warning-color, #ffa600);
    }
    .chip.bad {
      background: color-mix(in srgb, var(--error-color, #db4437) 18%, transparent);
      color: var(--error-color, #db4437);
    }
    button.link {
      flex: none;
      background: none;
      border: none;
      padding: 8px;
      /* Comfortably tappable: the rig gets edited on a tablet during a
         get-in, not with a mouse. */
      min-width: 44px;
      min-height: 44px;
      font: inherit;
      font-size: 0.9rem;
      color: var(--primary-color);
      cursor: pointer;
    }
    button.link:disabled {
      opacity: 0.5;
      cursor: default;
    }
    button.link.danger {
      color: var(--error-color, #db4437);
    }
    input[type="search"] {
      width: 100%;
      box-sizing: border-box;
      margin-top: 8px;
      padding: 10px 12px;
      font: inherit;
      color: var(--primary-text-color);
      background: var(--secondary-background-color);
      border: 1px solid var(--divider-color);
      border-radius: 8px;
    }
    .footer {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      padding: 8px 16px 12px;
      border-top: 1px solid var(--divider-color);
    }
    .stamp {
      font-family: var(--code-font-family, monospace);
      font-size: 0.75rem;
      color: var(--secondary-text-color);
    }
    .stamp.mismatch {
      color: var(--error-color, #db4437);
    }
  `,m([C({attribute:!1})],b.prototype,"hass",2),m([g()],b.prototype,"_config",2),m([g()],b.prototype,"_info",2),m([g()],b.prototype,"_rig",2),m([g()],b.prototype,"_bridge",2),m([g()],b.prototype,"_candidates",2),m([g()],b.prototype,"_error",2),m([g()],b.prototype,"_busy",2),m([g()],b.prototype,"_adding",2),m([g()],b.prototype,"_filter",2),m([g()],b.prototype,"_tab",2);V(Ct,b);Et({type:Ct,name:"Lighting Console",description:"Theatre lighting console \u2014 rig, cue list and effects.",preview:!1,documentationURL:"https://github.com/sremich/ha-lighting-console"});console.info("%c LIGHTING-CONSOLE %c 0.5.0 (4bda023d226d) ","color:#fff;background:#3b5bdb;font-weight:700","color:#3b5bdb;background:#eef");export{b as LightingConsoleCard};
