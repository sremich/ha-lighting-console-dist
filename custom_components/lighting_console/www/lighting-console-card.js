var kt=Object.defineProperty;var Ct=Object.getOwnPropertyDescriptor;var p=(s,e,t,r)=>{for(var i=r>1?void 0:r?Ct(e,t):e,n=s.length-1,o;n>=0;n--)(o=s[n])&&(i=(r?o(e,t,i):o(i))||i);return r&&i&&kt(e,t,i),i};var B=globalThis,L=B.ShadowRoot&&(B.ShadyCSS===void 0||B.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,V=Symbol(),ot=new WeakMap,T=class{constructor(e,t,r){if(this._$cssResult$=!0,r!==V)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(L&&e===void 0){let r=t!==void 0&&t.length===1;r&&(e=ot.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),r&&ot.set(t,e))}return e}toString(){return this.cssText}},at=s=>new T(typeof s=="string"?s:s+"",void 0,V),P=(s,...e)=>{let t=s.length===1?s[0]:e.reduce((r,i,n)=>r+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+s[n+1],s[0]);return new T(t,s,V)},lt=(s,e)=>{if(L)s.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let r=document.createElement("style"),i=B.litNonce;i!==void 0&&r.setAttribute("nonce",i),r.textContent=t.cssText,s.appendChild(r)}},K=L?s=>s:s=>s instanceof CSSStyleSheet?(e=>{let t="";for(let r of e.cssRules)t+=r.cssText;return at(t)})(s):s;var{is:Rt,defineProperty:Tt,getOwnPropertyDescriptor:Pt,getOwnPropertyNames:Nt,getOwnPropertySymbols:Ht,getPrototypeOf:Mt}=Object,j=globalThis,ct=j.trustedTypes,Ot=ct?ct.emptyScript:"",It=j.reactiveElementPolyfillSupport,N=(s,e)=>s,H={toAttribute(s,e){switch(e){case Boolean:s=s?Ot:null;break;case Object:case Array:s=s==null?s:JSON.stringify(s)}return s},fromAttribute(s,e){let t=s;switch(e){case Boolean:t=s!==null;break;case Number:t=s===null?null:Number(s);break;case Object:case Array:try{t=JSON.parse(s)}catch{t=null}}return t}},G=(s,e)=>!Rt(s,e),dt={attribute:!0,type:String,converter:H,reflect:!1,useDefault:!1,hasChanged:G};Symbol.metadata??=Symbol("metadata"),j.litPropertyMetadata??=new WeakMap;var y=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=dt){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let r=Symbol(),i=this.getPropertyDescriptor(e,r,t);i!==void 0&&Tt(this.prototype,e,i)}}static getPropertyDescriptor(e,t,r){let{get:i,set:n}=Pt(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:i,set(o){let c=i?.call(this);n?.call(this,o),this.requestUpdate(e,c,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??dt}static _$Ei(){if(this.hasOwnProperty(N("elementProperties")))return;let e=Mt(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(N("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(N("properties"))){let t=this.properties,r=[...Nt(t),...Ht(t)];for(let i of r)this.createProperty(i,t[i])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[r,i]of t)this.elementProperties.set(r,i)}this._$Eh=new Map;for(let[t,r]of this.elementProperties){let i=this._$Eu(t,r);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let r=new Set(e.flat(1/0).reverse());for(let i of r)t.unshift(K(i))}else e!==void 0&&t.push(K(e));return t}static _$Eu(e,t){let r=t.attribute;return r===!1?void 0:typeof r=="string"?r:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let r of t.keys())this.hasOwnProperty(r)&&(e.set(r,this[r]),delete this[r]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return lt(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,r){this._$AK(e,r)}_$ET(e,t){let r=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,r);if(i!==void 0&&r.reflect===!0){let n=(r.converter?.toAttribute!==void 0?r.converter:H).toAttribute(t,r.type);this._$Em=e,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(e,t){let r=this.constructor,i=r._$Eh.get(e);if(i!==void 0&&this._$Em!==i){let n=r.getPropertyOptions(i),o=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:H;this._$Em=i;let c=o.fromAttribute(t,n.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(e,t,r,i=!1,n){if(e!==void 0){let o=this.constructor;if(i===!1&&(n=this[e]),r??=o.getPropertyOptions(e),!((r.hasChanged??G)(n,t)||r.useDefault&&r.reflect&&n===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,r))))return;this.C(e,t,r)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:r,reflect:i,wrapped:n},o){r&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,o??t??this[e]),n!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||r||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,n]of this._$Ep)this[i]=n;this._$Ep=void 0}let r=this.constructor.elementProperties;if(r.size>0)for(let[i,n]of r){let{wrapped:o}=n,c=this[i];o!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,n,c)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(r=>r.hostUpdate?.()),this.update(t)):this._$EM()}catch(r){throw e=!1,this._$EM(),r}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};y.elementStyles=[],y.shadowRootOptions={mode:"open"},y[N("elementProperties")]=new Map,y[N("finalized")]=new Map,It?.({ReactiveElement:y}),(j.reactiveElementVersions??=[]).push("2.1.2");var et=globalThis,ht=s=>s,q=et.trustedTypes,pt=q?q.createPolicy("lit-html",{createHTML:s=>s}):void 0,bt="$lit$",x=`lit$${Math.random().toFixed(9).slice(2)}$`,vt="?"+x,Ut=`<${vt}>`,E=document,O=()=>E.createComment(""),I=s=>s===null||typeof s!="object"&&typeof s!="function",rt=Array.isArray,Dt=s=>rt(s)||typeof s?.[Symbol.iterator]=="function",J=`[ 	
\f\r]`,M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ut=/-->/g,gt=/>/g,w=RegExp(`>|${J}(?:([^\\s"'>=/]+)(${J}*=${J}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),mt=/'/g,ft=/"/g,yt=/^(?:script|style|textarea|title)$/i,it=s=>(e,...t)=>({_$litType$:s,strings:e,values:t}),a=it(1),Zt=it(2),Qt=it(3),A=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),_t=new WeakMap,S=E.createTreeWalker(E,129);function $t(s,e){if(!rt(s)||!s.hasOwnProperty("raw"))throw Error("invalid template strings array");return pt!==void 0?pt.createHTML(e):e}var zt=(s,e)=>{let t=s.length-1,r=[],i,n=e===2?"<svg>":e===3?"<math>":"",o=M;for(let c=0;c<t;c++){let l=s[c],h,m,u=-1,b=0;for(;b<l.length&&(o.lastIndex=b,m=o.exec(l),m!==null);)b=o.lastIndex,o===M?m[1]==="!--"?o=ut:m[1]!==void 0?o=gt:m[2]!==void 0?(yt.test(m[2])&&(i=RegExp("</"+m[2],"g")),o=w):m[3]!==void 0&&(o=w):o===w?m[0]===">"?(o=i??M,u=-1):m[1]===void 0?u=-2:(u=o.lastIndex-m[2].length,h=m[1],o=m[3]===void 0?w:m[3]==='"'?ft:mt):o===ft||o===mt?o=w:o===ut||o===gt?o=M:(o=w,i=void 0);let $=o===w&&s[c+1].startsWith("/>")?" ":"";n+=o===M?l+Ut:u>=0?(r.push(h),l.slice(0,u)+bt+l.slice(u)+x+$):l+x+(u===-2?c:$)}return[$t(s,n+(s[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),r]},U=class s{constructor({strings:e,_$litType$:t},r){let i;this.parts=[];let n=0,o=0,c=e.length-1,l=this.parts,[h,m]=zt(e,t);if(this.el=s.createElement(h,r),S.currentNode=this.el.content,t===2||t===3){let u=this.el.content.firstChild;u.replaceWith(...u.childNodes)}for(;(i=S.nextNode())!==null&&l.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let u of i.getAttributeNames())if(u.endsWith(bt)){let b=m[o++],$=i.getAttribute(u).split(x),z=/([.?@])?(.*)/.exec(b);l.push({type:1,index:n,name:z[2],strings:$,ctor:z[1]==="."?Z:z[1]==="?"?Q:z[1]==="@"?X:C}),i.removeAttribute(u)}else u.startsWith(x)&&(l.push({type:6,index:n}),i.removeAttribute(u));if(yt.test(i.tagName)){let u=i.textContent.split(x),b=u.length-1;if(b>0){i.textContent=q?q.emptyScript:"";for(let $=0;$<b;$++)i.append(u[$],O()),S.nextNode(),l.push({type:2,index:++n});i.append(u[b],O())}}}else if(i.nodeType===8)if(i.data===vt)l.push({type:2,index:n});else{let u=-1;for(;(u=i.data.indexOf(x,u+1))!==-1;)l.push({type:7,index:n}),u+=x.length-1}n++}}static createElement(e,t){let r=E.createElement("template");return r.innerHTML=e,r}};function k(s,e,t=s,r){if(e===A)return e;let i=r!==void 0?t._$Co?.[r]:t._$Cl,n=I(e)?void 0:e._$litDirective$;return i?.constructor!==n&&(i?._$AO?.(!1),n===void 0?i=void 0:(i=new n(s),i._$AT(s,t,r)),r!==void 0?(t._$Co??=[])[r]=i:t._$Cl=i),i!==void 0&&(e=k(s,i._$AS(s,e.values),i,r)),e}var Y=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:r}=this._$AD,i=(e?.creationScope??E).importNode(t,!0);S.currentNode=i;let n=S.nextNode(),o=0,c=0,l=r[0];for(;l!==void 0;){if(o===l.index){let h;l.type===2?h=new D(n,n.nextSibling,this,e):l.type===1?h=new l.ctor(n,l.name,l.strings,this,e):l.type===6&&(h=new tt(n,this,e)),this._$AV.push(h),l=r[++c]}o!==l?.index&&(n=S.nextNode(),o++)}return S.currentNode=E,i}p(e){let t=0;for(let r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(e,r,t),t+=r.strings.length-2):r._$AI(e[t])),t++}},D=class s{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,r,i){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=r,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=k(this,e,t),I(e)?e===d||e==null||e===""?(this._$AH!==d&&this._$AR(),this._$AH=d):e!==this._$AH&&e!==A&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Dt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==d&&I(this._$AH)?this._$AA.nextSibling.data=e:this.T(E.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:r}=e,i=typeof r=="number"?this._$AC(e):(r.el===void 0&&(r.el=U.createElement($t(r.h,r.h[0]),this.options)),r);if(this._$AH?._$AD===i)this._$AH.p(t);else{let n=new Y(i,this),o=n.u(this.options);n.p(t),this.T(o),this._$AH=n}}_$AC(e){let t=_t.get(e.strings);return t===void 0&&_t.set(e.strings,t=new U(e)),t}k(e){rt(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,r,i=0;for(let n of e)i===t.length?t.push(r=new s(this.O(O()),this.O(O()),this,this.options)):r=t[i],r._$AI(n),i++;i<t.length&&(this._$AR(r&&r._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let r=ht(e).nextSibling;ht(e).remove(),e=r}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},C=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,r,i,n){this.type=1,this._$AH=d,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=n,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=d}_$AI(e,t=this,r,i){let n=this.strings,o=!1;if(n===void 0)e=k(this,e,t,0),o=!I(e)||e!==this._$AH&&e!==A,o&&(this._$AH=e);else{let c=e,l,h;for(e=n[0],l=0;l<n.length-1;l++)h=k(this,c[r+l],t,l),h===A&&(h=this._$AH[l]),o||=!I(h)||h!==this._$AH[l],h===d?e=d:e!==d&&(e+=(h??"")+n[l+1]),this._$AH[l]=h}o&&!i&&this.j(e)}j(e){e===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},Z=class extends C{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===d?void 0:e}},Q=class extends C{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==d)}},X=class extends C{constructor(e,t,r,i,n){super(e,t,r,i,n),this.type=5}_$AI(e,t=this){if((e=k(this,e,t,0)??d)===A)return;let r=this._$AH,i=e===d&&r!==d||e.capture!==r.capture||e.once!==r.once||e.passive!==r.passive,n=e!==d&&(r===d||i);i&&this.element.removeEventListener(this.name,this,r),n&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},tt=class{constructor(e,t,r){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(e){k(this,e)}};var Bt=et.litHtmlPolyfillSupport;Bt?.(U,D),(et.litHtmlVersions??=[]).push("3.3.3");var xt=(s,e,t)=>{let r=t?.renderBefore??e,i=r._$litPart$;if(i===void 0){let n=t?.renderBefore??null;r._$litPart$=i=new D(e.insertBefore(O(),n),n,void 0,t??{})}return i._$AI(s),i};var st=globalThis,v=class extends y{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=xt(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return A}};v._$litElement$=!0,v.finalized=!0,st.litElementHydrateSupport?.({LitElement:v});var Lt=st.litElementPolyfillSupport;Lt?.({LitElement:v});(st.litElementVersions??=[]).push("4.2.2");var jt={attribute:!0,type:String,converter:H,reflect:!1,hasChanged:G},Gt=(s=jt,e,t)=>{let{kind:r,metadata:i}=t,n=globalThis.litPropertyMetadata.get(i);if(n===void 0&&globalThis.litPropertyMetadata.set(i,n=new Map),r==="setter"&&((s=Object.create(s)).wrapped=!0),n.set(t.name,s),r==="accessor"){let{name:o}=t;return{set(c){let l=e.get.call(this);e.set.call(this,c),this.requestUpdate(o,l,s,!0,c)},init(c){return c!==void 0&&this.C(o,void 0,s,c),c}}}if(r==="setter"){let{name:o}=t;return function(c){let l=this[o];e.call(this,c),this.requestUpdate(o,l,s,!0,c)}}throw Error("Unsupported decorator location: "+r)};function R(s){return(e,t)=>typeof t=="object"?Gt(s,e,t):((r,i,n)=>{let o=i.hasOwnProperty(n);return i.constructor.createProperty(n,r),o?Object.getOwnPropertyDescriptor(i,n):void 0})(s,e,t)}function g(s){return R({...s,state:!0,attribute:!1})}function W(s,e){customElements.get(s)||customElements.define(s,e)}function wt(s){window.customCards=window.customCards??[],window.customCards.some(e=>e.type===s.type)||window.customCards.push(s)}var St={unavailable:{label:"Unavailable",tone:"bad"},hue_color_no_area:{label:"Not in an area",tone:"warn"},streamable:{label:"Effects",tone:"good"},rest_only:{label:"Home Assistant",tone:"neutral"}},Et=[0,.5,1,2,3,5,10,20,30];function nt(s){return s<=0?"snap":s<1?`${s}s`:`${Number.isInteger(s)?s:s.toFixed(1)}s`}var f=class extends v{constructor(){super(...arguments);this._effects=[];this._busy=!1;this._creatingShow=!1;this._newShowName="";this._importing=!1;this._addingEffect=!1;this._draftParams={};this._createShow=()=>{let t=this._newShowName.trim();t&&(this._run("lighting_console/shows/create",{name:t}),this._newShowName="",this._creatingShow=!1)};this._deleteShow=()=>{let t=this._show;if(!t)return;confirm(`Delete "${t.name}" and all ${t.cues.length} of its cues?

This cannot be undone.`)&&this._run("lighting_console/shows/delete",{show_id:t.id})};this._openImport=()=>{this._importing=!0,this._importGroups=void 0,(async()=>{try{let t=await this._call("lighting_console/import/groups");this._importGroups=t.groups}catch(t){this._error=t instanceof Error?t.message:String(t),this._importing=!1}})()};this._previewDraft=()=>{this._draftEffect&&(async()=>{try{await this._call("lighting_console/effects/preview",{effect:this._draftEffect,params:this._draftParams}),this._summary=await this._call("lighting_console/shows/list")}catch(t){this._error=t instanceof Error?t.message:String(t)}})()};this._saveDraft=()=>{this._draftEffect&&(this._run("lighting_console/cues/add_effect",{effect:this._draftEffect,params:this._draftParams}),this._addingEffect=!1,this._draftEffect=void 0)}}updated(t){t.has("hass")&&this.hass&&!this._summary&&!this._error&&this._load()}async _call(t,r={}){return this.hass.callWS({type:t,...r})}async _load(){try{let[t,r,i]=await Promise.all([this._call("lighting_console/shows/list"),this._call("lighting_console/effects/list"),this._call("lighting_console/rig/list")]);this._summary=t,this._effects=r.effects,this._rig=i,this._error=void 0}catch(t){this._error=t instanceof Error?t.message:String(t)}}_run(t,r={}){this._busy||(this._busy=!0,(async()=>{try{this._summary=await this._call(t,r),this._error=void 0}catch(i){this._error=i instanceof Error?i.message:String(i)}finally{this._busy=!1}})())}get _show(){return this._summary?.active_show??null}get _cues(){return this._show?.cues??[]}render(){return this._error?a`<div class="error">
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
          @change=${r=>this._run("lighting_console/shows/activate",{show_id:r.target.value})}
        >
          ${t.shows.map(r=>a`<option value=${r.id}>
              ${r.name} · ${r.cue_count} cue${r.cue_count===1?"":"s"}
            </option>`)}
        </select>
        <button @click=${()=>this._creatingShow=!0}>New show</button>
        <button @click=${this._openImport}>Import from Hue</button>
        ${this._show?a`<button
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
    `}_runImport(t){this._run("lighting_console/import/run",{group_id:t.id,name:t.name,default_fade:0}),this._importing=!1}_renderConsole(){let t=this._summary.playback,r=this._cues,i=t.current_index===null?null:r[t.current_index]??null,n=t.current_index===null?r[0]:r[t.current_index+1];return a`
      <div class="transport">
        <button
          class="go"
          ?disabled=${this._busy||!n}
          @click=${()=>this._run("lighting_console/playback/go")}
        >
          <span class="golabel">GO</span>
          <span class="gonext">${n?n.label:"end of show"}</span>
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
          <b>${i?`${i.label}${i.name?` \u2014 ${i.name}`:""}`:"nothing"}</b></span
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
      ${r.length===0?this._renderNoCues():this._renderCues(r,t.current_cue_id)}
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
    `}_renderCues(t,r){return a`
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
          ${t.map((i,n)=>this._renderCueRow(i,n,r))}
        </tbody>
      </table>
    `}_renderCueRow(t,r,i){let n=t.id===i,o=t.id===this._editingCueId;return a`
      <tr
        class=${`cue ${n?"live":""} ${o?"editing":""}`}
        draggable="true"
        @dragstart=${()=>this._dragFrom=r}
        @dragover=${c=>c.preventDefault()}
        @drop=${()=>this._dropOn(r)}
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
        <td class="c-fade">${t.kind==="effect"?"\u2014":nt(t.fade)}</td>
        <td class="c-actions">
          <button title="Move up" ?disabled=${r===0} @click=${()=>this._move(r,-1)}>↑</button>
          <button title="Move down" ?disabled=${r===this._cues.length-1} @click=${()=>this._move(r,1)}>↓</button>
          <button title="Edit" @click=${()=>this._editingCueId=o?void 0:t.id}>Edit</button>
        </td>
      </tr>
      ${o?a`<tr class="editorrow"><td colspan="4">${this._renderCueEditor(t,r)}</td></tr>`:d}
    `}_renderCueEditor(t,r){return a`
      <div class="editor">
        <div class="row">
          <label class="grow">
            Cue number
            <input
              .value=${t.label}
              @change=${i=>this._update(t.id,{label:i.target.value})}
            />
          </label>
          <label class="grow2">
            Name
            <input
              .value=${t.name}
              placeholder="what this cue is for"
              @change=${i=>this._update(t.id,{name:i.target.value})}
            />
          </label>
        </div>

        ${t.kind==="look"?a`
              <div class="row wrap">
                <span class="fadelabel">Fade</span>
                ${Et.map(i=>a`<button
                    class=${t.fade===i?"chip on":"chip"}
                    @click=${()=>this._update(t.id,{fade:i})}
                  >
                    ${nt(i)}
                  </button>`)}
                <input
                  class="fadeinput"
                  type="number"
                  min="0"
                  step="0.05"
                  .value=${String(t.fade)}
                  @change=${i=>this._update(t.id,{fade:Number(i.target.value)})}
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
                  >${t.levels.filter(i=>i.state==="on").length} of
                  ${t.levels.length} lights on</span
                >
              </div>
            `:this._renderEffectParams(t.effect??"",t.effect_params,i=>this._update(t.id,{effect_params:i}))}

        ${t.notes?a`<div class="muted notes">${t.notes}</div>`:d}

        <div class="row">
          <button @click=${()=>this._insertAfter(r)}>
            Insert a cue after this one
          </button>
          <button class="danger-text" @click=${()=>this._deleteCue(t)}>
            Delete ${t.label}
          </button>
        </div>
      </div>
    `}_renderEffectDraft(){let t=this._effects.find(r=>r.name===this._draftEffect);return a`
      <div class="panel">
        <h4>Effect cue</h4>
        <div class="row wrap">
          ${this._effects.map(r=>a`<button
              class=${r.name===this._draftEffect?"chip on":"chip"}
              @click=${()=>{this._draftEffect=r.name,this._draftParams=Object.fromEntries(r.params.map(i=>[i.key,i.default]))}}
            >
              ${r.label}
            </button>`)}
        </div>
        ${t?a`
              <p class="muted">${t.description}</p>
              ${this._renderEffectParams(t.name,this._draftParams,r=>{this._draftParams=r})}
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
    `}_renderEffectParams(t,r,i){let n=this._effects.find(c=>c.name===t);if(!n)return a`<div class="muted">Unknown effect.</div>`;let o=(c,l)=>i({...r,[c]:l});return a`
      <div class="params">
        ${n.params.map(c=>this._renderParam(c,r,o))}
      </div>
    `}_renderParam(t,r,i){let n=r[t.key]??t.default;if(t.type==="number")return a`<label>
        ${t.label}${t.unit?` (${t.unit})`:""}
        <input
          type="number"
          .value=${String(n??"")}
          min=${t.minimum??d}
          max=${t.maximum??d}
          step=${t.step??d}
          @change=${o=>i(t.key,Number(o.target.value))}
        />
        ${t.help?a`<small class="muted">${t.help}</small>`:d}
      </label>`;if(t.type==="select")return a`<label>
        ${t.label}
        <select
          .value=${String(n??"")}
          @change=${o=>i(t.key,o.target.value)}
        >
          ${t.options.map(o=>a`<option value=${o}>${o}</option>`)}
        </select>
      </label>`;if(t.type==="color"){let o=n??[[255,255,255]];return a`<label>
        ${t.label}
        <span class="colors">
          ${o.map((c,l)=>a`<input
              type="color"
              .value=${qt(c)}
              @change=${h=>{let m=o.map((u,b)=>b===l?Ft(h.target.value):u);i(t.key,m)}}
            />`)}
          <button
            class="chip"
            title="Add another colour to cycle through"
            @click=${()=>i(t.key,[...o,[255,255,255]])}
          >
            +
          </button>
          ${o.length>1?a`<button class="chip" @click=${()=>i(t.key,o.slice(0,-1))}>
                −
              </button>`:d}
        </span>
        ${t.help?a`<small class="muted">${t.help}</small>`:d}
      </label>`}if(t.type==="entities"){let o=(n??[]).filter(h=>typeof h=="string"),c=this._rig?.members??[],l=h=>i(t.key,o.includes(h)?o.filter(m=>m!==h):[...o,h]);return a`<label class="wide">
        ${t.label}
        <span class="targets">
          ${c.length===0?a`<small class="muted"
                >No lights in the rig yet — add them on the Rig tab.</small
              >`:c.map(h=>{let m=o.indexOf(h.entity_id);return a`<button
                  class=${m>=0?"chip on":"chip"}
                  title=${h.entity_id}
                  @click=${()=>l(h.entity_id)}
                >
                  ${m>=0?a`<span class="ord">${m+1}</span>`:d}${h.name}
                </button>`})}
        </span>
        <span class="targets">
          <button class="chip" @click=${()=>i(t.key,[])}>
            Whole rig
          </button>
          <button
            class="chip"
            @click=${()=>i(t.key,c.map(h=>h.entity_id))}
          >
            All, in rig order
          </button>
          ${o.length>1?a`<button
                class="chip"
                title="Walk them the other way"
                @click=${()=>i(t.key,[...o].reverse())}
              >
                Reverse
              </button>`:d}
        </span>
        <small class="muted">
          ${o.length===0?"Empty means the whole rig, in rig order.":`${o.length} light${o.length===1?"":"s"}, driven in the order shown.`}
        </small>
      </label>`}return a`<label>
      ${t.label}
      <input
        type="checkbox"
        .checked=${!!n}
        @change=${o=>i(t.key,o.target.checked)}
      />
    </label>`}_stopEffect(){(async()=>{try{await this._call("lighting_console/effects/stop"),this._summary=await this._call("lighting_console/shows/list")}catch(t){this._error=t instanceof Error?t.message:String(t)}})()}_update(t,r){this._run("lighting_console/cues/update",{cue_id:t,changes:r})}_deleteCue(t){confirm(`Delete ${t.label}?`)&&(this._editingCueId=void 0,this._run("lighting_console/cues/delete",{cue_id:t.id}))}_insertAfter(t){this._run("lighting_console/cues/record",{at:t+1})}_move(t,r){let i=this._cues.map(o=>o.id),n=t+r;n<0||n>=i.length||([i[t],i[n]]=[i[n],i[t]],this._run("lighting_console/cues/reorder",{cue_ids:i}))}_dropOn(t){let r=this._dragFrom;if(this._dragFrom=void 0,r===void 0||r===t)return;let i=this._cues.map(o=>o.id),[n]=i.splice(r,1);i.splice(t,0,n),this._run("lighting_console/cues/reorder",{cue_ids:i})}};f.styles=P`
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
      width: 8ch;
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
      padding: 2px 6px;
      font-size: 0.85em;
    }
    .labelbtn {
      border: none;
      background: none;
      padding: 2px 4px;
      font-weight: 600;
      color: var(--primary-text-color);
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
      padding: 3px 9px;
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
    label.wide {
      grid-column: 1 / -1;
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
    .colors input[type="color"] {
      width: 34px;
      height: 30px;
      padding: 2px;
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
  `,p([R({attribute:!1})],f.prototype,"hass",2),p([g()],f.prototype,"_summary",2),p([g()],f.prototype,"_effects",2),p([g()],f.prototype,"_rig",2),p([g()],f.prototype,"_error",2),p([g()],f.prototype,"_busy",2),p([g()],f.prototype,"_creatingShow",2),p([g()],f.prototype,"_newShowName",2),p([g()],f.prototype,"_importing",2),p([g()],f.prototype,"_importGroups",2),p([g()],f.prototype,"_editingCueId",2),p([g()],f.prototype,"_addingEffect",2),p([g()],f.prototype,"_draftEffect",2),p([g()],f.prototype,"_draftParams",2),p([g()],f.prototype,"_dragFrom",2);function qt(s){let[e,t,r]=s;return`#${[e,t,r].map(i=>Math.max(0,Math.min(255,i)).toString(16).padStart(2,"0")).join("")}`}function Ft(s){let e=s.replace("#","");return[parseInt(e.slice(0,2),16),parseInt(e.slice(2,4),16),parseInt(e.slice(4,6),16)]}W("lighting-console-cues",f);var At="lighting-console-card",_=class extends v{constructor(){super(...arguments);this._busy=!1;this._adding=!1;this._filter="";this._tab="show"}setConfig(t){this._config=t}getCardSize(){return 12}updated(t){t.has("hass")&&this.hass&&!this._info&&!this._error&&this._load()}async _call(t,r={}){return this.hass.callWS({type:t,...r})}async _load(){try{let[t,r,i]=await Promise.all([this._call("lighting_console/info"),this._call("lighting_console/rig/list"),this._call("lighting_console/bridge/status")]);this._info=t,this._rig=r,this._bridge=i,this._error=void 0}catch(t){this._error=t instanceof Error?t.message:String(t)}}async _withBusy(t){this._busy=!0;try{await t(),this._error=void 0}catch(r){this._error=r instanceof Error?r.message:String(r)}finally{this._busy=!1}}_refreshBridge(){this._withBusy(async()=>{let t=await this._call("lighting_console/bridge/refresh");this._bridge=t,this._rig=t.rig})}_remove(t){this._withBusy(async()=>{this._rig=await this._call("lighting_console/rig/remove",{entity_ids:[t]})})}_add(t){this._withBusy(async()=>{this._rig=await this._call("lighting_console/rig/add",{entity_ids:[t]}),this._candidates=this._candidates?.filter(r=>r.entity_id!==t)})}_openAdd(){this._adding=!0,this._withBusy(async()=>{let t=await this._call("lighting_console/rig/candidates");this._candidates=t.candidates})}render(){return!this._config||!this.hass?d:a`
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
    `}_renderTabs(){let t=(r,i,n)=>a`
      <button
        class=${this._tab===r?"tab on":"tab"}
        title=${n}
        @click=${()=>this._tab=r}
      >
        ${i}
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
                ${t.entertainment_areas.map(r=>a`
                    <li>
                      <span class="area-name">${r.name}</span>
                      <span class="detail">
                        ${r.light_count}
                        ${r.light_count===1?"light":"lights"} ·
                        ${r.channel_count}
                        ${r.channel_count===1?"channel":"channels"}
                      </span>
                      ${r.streaming?a`<span class="chip good">streaming</span>`:d}
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
                ${t.members.map(r=>this._renderMember(r))}
              </ul>
            `}
      </section>
    `}_renderMember(t){let r=St[t.capability];return a`
      <li>
        <div class="member">
          <span class="member-name">${t.name}</span>
          <span class="entity-id">${t.entity_id}</span>
          <span class="detail">${t.reason}</span>
        </div>
        <span class="chip ${r.tone}">${r.label}</span>
        <button
          class="link danger"
          ?disabled=${this._busy}
          title="Remove from the rig"
          @click=${()=>this._remove(t.entity_id)}
        >
          Remove
        </button>
      </li>
    `}_renderCandidates(){let t=this._filter.trim().toLowerCase(),r=(this._candidates??[]).filter(i=>!t||i.name.toLowerCase().includes(t)||i.entity_id.toLowerCase().includes(t));return a`
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
          @input=${i=>{this._filter=i.target.value}}
        />
        ${r.length===0?a`<p class="detail">Nothing left to add.</p>`:a`
              <ul class="rig">
                ${r.map(i=>a`
                    <li>
                      <div class="member">
                        <span class="member-name">${i.name}</span>
                        <span class="entity-id">${i.entity_id}</span>
                      </div>
                      <button
                        class="link"
                        ?disabled=${this._busy}
                        @click=${()=>this._add(i.entity_id)}
                      >
                        Add
                      </button>
                    </li>
                  `)}
              </ul>
            `}
      </section>
    `}_renderBuildStamp(){let t=this._info?`${this._info.version} \xB7 ${this._info.git_sha}`:"\u2014",r="0.3.2 \xB7 38b33f1adc75",i=this._info!==void 0&&this._info.version!=="0.3.2";return a`
      <span class="stamp ${i?"mismatch":""}">
        card ${r} / backend ${t}
      </span>
      ${i?a`<span class="warn-text" title="Card and integration versions differ">
            version mismatch
          </span>`:d}
    `}};_.styles=P`
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
  `,p([R({attribute:!1})],_.prototype,"hass",2),p([g()],_.prototype,"_config",2),p([g()],_.prototype,"_info",2),p([g()],_.prototype,"_rig",2),p([g()],_.prototype,"_bridge",2),p([g()],_.prototype,"_candidates",2),p([g()],_.prototype,"_error",2),p([g()],_.prototype,"_busy",2),p([g()],_.prototype,"_adding",2),p([g()],_.prototype,"_filter",2),p([g()],_.prototype,"_tab",2);W(At,_);wt({type:At,name:"Lighting Console",description:"Theatre lighting console \u2014 rig, cue list and effects.",preview:!1,documentationURL:"https://github.com/sremich/ha-lighting-console"});console.info("%c LIGHTING-CONSOLE %c 0.3.2 (38b33f1adc75) ","color:#fff;background:#3b5bdb;font-weight:700","color:#3b5bdb;background:#eef");export{_ as LightingConsoleCard};
