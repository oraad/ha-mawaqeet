/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const B = globalThis, te = B.ShadowRoot && (B.ShadyCSS === void 0 || B.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, ie = Symbol(), he = /* @__PURE__ */ new WeakMap();
let Ae = class {
  constructor(e, t, s) {
    if (this._$cssResult$ = !0, s !== ie) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = e, this.t = t;
  }
  get styleSheet() {
    let e = this.o;
    const t = this.t;
    if (te && e === void 0) {
      const s = t !== void 0 && t.length === 1;
      s && (e = he.get(t)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), s && he.set(t, e));
    }
    return e;
  }
  toString() {
    return this.cssText;
  }
};
const Ue = (i) => new Ae(typeof i == "string" ? i : i + "", void 0, ie), qe = (i, ...e) => {
  const t = i.length === 1 ? i[0] : e.reduce((s, r, n) => s + ((o) => {
    if (o._$cssResult$ === !0) return o.cssText;
    if (typeof o == "number") return o;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + o + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(r) + i[n + 1], i[0]);
  return new Ae(t, i, ie);
}, ze = (i, e) => {
  if (te) i.adoptedStyleSheets = e.map((t) => t instanceof CSSStyleSheet ? t : t.styleSheet);
  else for (const t of e) {
    const s = document.createElement("style"), r = B.litNonce;
    r !== void 0 && s.setAttribute("nonce", r), s.textContent = t.cssText, i.appendChild(s);
  }
}, de = te ? (i) => i : (i) => i instanceof CSSStyleSheet ? ((e) => {
  let t = "";
  for (const s of e.cssRules) t += s.cssText;
  return Ue(t);
})(i) : i;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const { is: De, defineProperty: He, getOwnPropertyDescriptor: Re, getOwnPropertyNames: Le, getOwnPropertySymbols: je, getPrototypeOf: Ie } = Object, g = globalThis, ue = g.trustedTypes, Be = ue ? ue.emptyScript : "", J = g.reactiveElementPolyfillSupport, M = (i, e) => i, V = { toAttribute(i, e) {
  switch (e) {
    case Boolean:
      i = i ? Be : null;
      break;
    case Object:
    case Array:
      i = i == null ? i : JSON.stringify(i);
  }
  return i;
}, fromAttribute(i, e) {
  let t = i;
  switch (e) {
    case Boolean:
      t = i !== null;
      break;
    case Number:
      t = i === null ? null : Number(i);
      break;
    case Object:
    case Array:
      try {
        t = JSON.parse(i);
      } catch {
        t = null;
      }
  }
  return t;
} }, se = (i, e) => !De(i, e), pe = { attribute: !0, type: String, converter: V, reflect: !1, useDefault: !1, hasChanged: se };
Symbol.metadata ?? (Symbol.metadata = Symbol("metadata")), g.litPropertyMetadata ?? (g.litPropertyMetadata = /* @__PURE__ */ new WeakMap());
let A = class extends HTMLElement {
  static addInitializer(e) {
    this._$Ei(), (this.l ?? (this.l = [])).push(e);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(e, t = pe) {
    if (t.state && (t.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(e) && ((t = Object.create(t)).wrapped = !0), this.elementProperties.set(e, t), !t.noAccessor) {
      const s = Symbol(), r = this.getPropertyDescriptor(e, s, t);
      r !== void 0 && He(this.prototype, e, r);
    }
  }
  static getPropertyDescriptor(e, t, s) {
    const { get: r, set: n } = Re(this.prototype, e) ?? { get() {
      return this[t];
    }, set(o) {
      this[t] = o;
    } };
    return { get: r, set(o) {
      const c = r == null ? void 0 : r.call(this);
      n == null || n.call(this, o), this.requestUpdate(e, c, s);
    }, configurable: !0, enumerable: !0 };
  }
  static getPropertyOptions(e) {
    return this.elementProperties.get(e) ?? pe;
  }
  static _$Ei() {
    if (this.hasOwnProperty(M("elementProperties"))) return;
    const e = Ie(this);
    e.finalize(), e.l !== void 0 && (this.l = [...e.l]), this.elementProperties = new Map(e.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(M("finalized"))) return;
    if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(M("properties"))) {
      const t = this.properties, s = [...Le(t), ...je(t)];
      for (const r of s) this.createProperty(r, t[r]);
    }
    const e = this[Symbol.metadata];
    if (e !== null) {
      const t = litPropertyMetadata.get(e);
      if (t !== void 0) for (const [s, r] of t) this.elementProperties.set(s, r);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [t, s] of this.elementProperties) {
      const r = this._$Eu(t, s);
      r !== void 0 && this._$Eh.set(r, t);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(e) {
    const t = [];
    if (Array.isArray(e)) {
      const s = new Set(e.flat(1 / 0).reverse());
      for (const r of s) t.unshift(de(r));
    } else e !== void 0 && t.push(de(e));
    return t;
  }
  static _$Eu(e, t) {
    const s = t.attribute;
    return s === !1 ? void 0 : typeof s == "string" ? s : typeof e == "string" ? e.toLowerCase() : void 0;
  }
  constructor() {
    super(), this._$Ep = void 0, this.isUpdatePending = !1, this.hasUpdated = !1, this._$Em = null, this._$Ev();
  }
  _$Ev() {
    var e;
    this._$ES = new Promise((t) => this.enableUpdating = t), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), (e = this.constructor.l) == null || e.forEach((t) => t(this));
  }
  addController(e) {
    var t;
    (this._$EO ?? (this._$EO = /* @__PURE__ */ new Set())).add(e), this.renderRoot !== void 0 && this.isConnected && ((t = e.hostConnected) == null || t.call(e));
  }
  removeController(e) {
    var t;
    (t = this._$EO) == null || t.delete(e);
  }
  _$E_() {
    const e = /* @__PURE__ */ new Map(), t = this.constructor.elementProperties;
    for (const s of t.keys()) this.hasOwnProperty(s) && (e.set(s, this[s]), delete this[s]);
    e.size > 0 && (this._$Ep = e);
  }
  createRenderRoot() {
    const e = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return ze(e, this.constructor.elementStyles), e;
  }
  connectedCallback() {
    var e;
    this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this.enableUpdating(!0), (e = this._$EO) == null || e.forEach((t) => {
      var s;
      return (s = t.hostConnected) == null ? void 0 : s.call(t);
    });
  }
  enableUpdating(e) {
  }
  disconnectedCallback() {
    var e;
    (e = this._$EO) == null || e.forEach((t) => {
      var s;
      return (s = t.hostDisconnected) == null ? void 0 : s.call(t);
    });
  }
  attributeChangedCallback(e, t, s) {
    this._$AK(e, s);
  }
  _$ET(e, t) {
    var n;
    const s = this.constructor.elementProperties.get(e), r = this.constructor._$Eu(e, s);
    if (r !== void 0 && s.reflect === !0) {
      const o = (((n = s.converter) == null ? void 0 : n.toAttribute) !== void 0 ? s.converter : V).toAttribute(t, s.type);
      this._$Em = e, o == null ? this.removeAttribute(r) : this.setAttribute(r, o), this._$Em = null;
    }
  }
  _$AK(e, t) {
    var n, o;
    const s = this.constructor, r = s._$Eh.get(e);
    if (r !== void 0 && this._$Em !== r) {
      const c = s.getPropertyOptions(r), a = typeof c.converter == "function" ? { fromAttribute: c.converter } : ((n = c.converter) == null ? void 0 : n.fromAttribute) !== void 0 ? c.converter : V;
      this._$Em = r;
      const l = a.fromAttribute(t, c.type);
      this[r] = l ?? ((o = this._$Ej) == null ? void 0 : o.get(r)) ?? l, this._$Em = null;
    }
  }
  requestUpdate(e, t, s, r = !1, n) {
    var o;
    if (e !== void 0) {
      const c = this.constructor;
      if (r === !1 && (n = this[e]), s ?? (s = c.getPropertyOptions(e)), !((s.hasChanged ?? se)(n, t) || s.useDefault && s.reflect && n === ((o = this._$Ej) == null ? void 0 : o.get(e)) && !this.hasAttribute(c._$Eu(e, s)))) return;
      this.C(e, t, s);
    }
    this.isUpdatePending === !1 && (this._$ES = this._$EP());
  }
  C(e, t, { useDefault: s, reflect: r, wrapped: n }, o) {
    s && !(this._$Ej ?? (this._$Ej = /* @__PURE__ */ new Map())).has(e) && (this._$Ej.set(e, o ?? t ?? this[e]), n !== !0 || o !== void 0) || (this._$AL.has(e) || (this.hasUpdated || s || (t = void 0), this._$AL.set(e, t)), r === !0 && this._$Em !== e && (this._$Eq ?? (this._$Eq = /* @__PURE__ */ new Set())).add(e));
  }
  async _$EP() {
    this.isUpdatePending = !0;
    try {
      await this._$ES;
    } catch (t) {
      Promise.reject(t);
    }
    const e = this.scheduleUpdate();
    return e != null && await e, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    var s;
    if (!this.isUpdatePending) return;
    if (!this.hasUpdated) {
      if (this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this._$Ep) {
        for (const [n, o] of this._$Ep) this[n] = o;
        this._$Ep = void 0;
      }
      const r = this.constructor.elementProperties;
      if (r.size > 0) for (const [n, o] of r) {
        const { wrapped: c } = o, a = this[n];
        c !== !0 || this._$AL.has(n) || a === void 0 || this.C(n, void 0, o, a);
      }
    }
    let e = !1;
    const t = this._$AL;
    try {
      e = this.shouldUpdate(t), e ? (this.willUpdate(t), (s = this._$EO) == null || s.forEach((r) => {
        var n;
        return (n = r.hostUpdate) == null ? void 0 : n.call(r);
      }), this.update(t)) : this._$EM();
    } catch (r) {
      throw e = !1, this._$EM(), r;
    }
    e && this._$AE(t);
  }
  willUpdate(e) {
  }
  _$AE(e) {
    var t;
    (t = this._$EO) == null || t.forEach((s) => {
      var r;
      return (r = s.hostUpdated) == null ? void 0 : r.call(s);
    }), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(e)), this.updated(e);
  }
  _$EM() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$ES;
  }
  shouldUpdate(e) {
    return !0;
  }
  update(e) {
    this._$Eq && (this._$Eq = this._$Eq.forEach((t) => this._$ET(t, this[t]))), this._$EM();
  }
  updated(e) {
  }
  firstUpdated(e) {
  }
};
A.elementStyles = [], A.shadowRootOptions = { mode: "open" }, A[M("elementProperties")] = /* @__PURE__ */ new Map(), A[M("finalized")] = /* @__PURE__ */ new Map(), J == null || J({ ReactiveElement: A }), (g.reactiveElementVersions ?? (g.reactiveElementVersions = [])).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const N = globalThis, me = (i) => i, K = N.trustedTypes, fe = K ? K.createPolicy("lit-html", { createHTML: (i) => i }) : void 0, Ee = "$lit$", $ = `lit$${Math.random().toFixed(9).slice(2)}$`, Se = "?" + $, Ve = `<${Se}>`, b = document, U = () => b.createComment(""), q = (i) => i === null || typeof i != "object" && typeof i != "function", re = Array.isArray, Ke = (i) => re(i) || typeof (i == null ? void 0 : i[Symbol.iterator]) == "function", X = `[ 	
\f\r]`, O = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, _e = /-->/g, $e = />/g, y = RegExp(`>|${X}(?:([^\\s"'>=/]+)(${X}*=${X}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g"), ge = /'/g, ye = /"/g, Ce = /^(?:script|style|textarea|title)$/i, We = (i) => (e, ...t) => ({ _$litType$: i, strings: e, values: t }), m = We(1), S = Symbol.for("lit-noChange"), p = Symbol.for("lit-nothing"), ve = /* @__PURE__ */ new WeakMap(), v = b.createTreeWalker(b, 129);
function Pe(i, e) {
  if (!re(i) || !i.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return fe !== void 0 ? fe.createHTML(e) : e;
}
const Fe = (i, e) => {
  const t = i.length - 1, s = [];
  let r, n = e === 2 ? "<svg>" : e === 3 ? "<math>" : "", o = O;
  for (let c = 0; c < t; c++) {
    const a = i[c];
    let l, d, h = -1, u = 0;
    for (; u < a.length && (o.lastIndex = u, d = o.exec(a), d !== null); ) u = o.lastIndex, o === O ? d[1] === "!--" ? o = _e : d[1] !== void 0 ? o = $e : d[2] !== void 0 ? (Ce.test(d[2]) && (r = RegExp("</" + d[2], "g")), o = y) : d[3] !== void 0 && (o = y) : o === y ? d[0] === ">" ? (o = r ?? O, h = -1) : d[1] === void 0 ? h = -2 : (h = o.lastIndex - d[2].length, l = d[1], o = d[3] === void 0 ? y : d[3] === '"' ? ye : ge) : o === ye || o === ge ? o = y : o === _e || o === $e ? o = O : (o = y, r = void 0);
    const f = o === y && i[c + 1].startsWith("/>") ? " " : "";
    n += o === O ? a + Ve : h >= 0 ? (s.push(l), a.slice(0, h) + Ee + a.slice(h) + $ + f) : a + $ + (h === -2 ? c : f);
  }
  return [Pe(i, n + (i[t] || "<?>") + (e === 2 ? "</svg>" : e === 3 ? "</math>" : "")), s];
};
class z {
  constructor({ strings: e, _$litType$: t }, s) {
    let r;
    this.parts = [];
    let n = 0, o = 0;
    const c = e.length - 1, a = this.parts, [l, d] = Fe(e, t);
    if (this.el = z.createElement(l, s), v.currentNode = this.el.content, t === 2 || t === 3) {
      const h = this.el.content.firstChild;
      h.replaceWith(...h.childNodes);
    }
    for (; (r = v.nextNode()) !== null && a.length < c; ) {
      if (r.nodeType === 1) {
        if (r.hasAttributes()) for (const h of r.getAttributeNames()) if (h.endsWith(Ee)) {
          const u = d[o++], f = r.getAttribute(h).split($), _ = /([.?@])?(.*)/.exec(u);
          a.push({ type: 1, index: n, name: _[2], strings: f, ctor: _[1] === "." ? Ge : _[1] === "?" ? Ze : _[1] === "@" ? Je : Y }), r.removeAttribute(h);
        } else h.startsWith($) && (a.push({ type: 6, index: n }), r.removeAttribute(h));
        if (Ce.test(r.tagName)) {
          const h = r.textContent.split($), u = h.length - 1;
          if (u > 0) {
            r.textContent = K ? K.emptyScript : "";
            for (let f = 0; f < u; f++) r.append(h[f], U()), v.nextNode(), a.push({ type: 2, index: ++n });
            r.append(h[u], U());
          }
        }
      } else if (r.nodeType === 8) if (r.data === Se) a.push({ type: 2, index: n });
      else {
        let h = -1;
        for (; (h = r.data.indexOf($, h + 1)) !== -1; ) a.push({ type: 7, index: n }), h += $.length - 1;
      }
      n++;
    }
  }
  static createElement(e, t) {
    const s = b.createElement("template");
    return s.innerHTML = e, s;
  }
}
function C(i, e, t = i, s) {
  var o, c;
  if (e === S) return e;
  let r = s !== void 0 ? (o = t._$Co) == null ? void 0 : o[s] : t._$Cl;
  const n = q(e) ? void 0 : e._$litDirective$;
  return (r == null ? void 0 : r.constructor) !== n && ((c = r == null ? void 0 : r._$AO) == null || c.call(r, !1), n === void 0 ? r = void 0 : (r = new n(i), r._$AT(i, t, s)), s !== void 0 ? (t._$Co ?? (t._$Co = []))[s] = r : t._$Cl = r), r !== void 0 && (e = C(i, r._$AS(i, e.values), r, s)), e;
}
class Ye {
  constructor(e, t) {
    this._$AV = [], this._$AN = void 0, this._$AD = e, this._$AM = t;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(e) {
    const { el: { content: t }, parts: s } = this._$AD, r = ((e == null ? void 0 : e.creationScope) ?? b).importNode(t, !0);
    v.currentNode = r;
    let n = v.nextNode(), o = 0, c = 0, a = s[0];
    for (; a !== void 0; ) {
      if (o === a.index) {
        let l;
        a.type === 2 ? l = new D(n, n.nextSibling, this, e) : a.type === 1 ? l = new a.ctor(n, a.name, a.strings, this, e) : a.type === 6 && (l = new Xe(n, this, e)), this._$AV.push(l), a = s[++c];
      }
      o !== (a == null ? void 0 : a.index) && (n = v.nextNode(), o++);
    }
    return v.currentNode = b, r;
  }
  p(e) {
    let t = 0;
    for (const s of this._$AV) s !== void 0 && (s.strings !== void 0 ? (s._$AI(e, s, t), t += s.strings.length - 2) : s._$AI(e[t])), t++;
  }
}
class D {
  get _$AU() {
    var e;
    return ((e = this._$AM) == null ? void 0 : e._$AU) ?? this._$Cv;
  }
  constructor(e, t, s, r) {
    this.type = 2, this._$AH = p, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = s, this.options = r, this._$Cv = (r == null ? void 0 : r.isConnected) ?? !0;
  }
  get parentNode() {
    let e = this._$AA.parentNode;
    const t = this._$AM;
    return t !== void 0 && (e == null ? void 0 : e.nodeType) === 11 && (e = t.parentNode), e;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(e, t = this) {
    e = C(this, e, t), q(e) ? e === p || e == null || e === "" ? (this._$AH !== p && this._$AR(), this._$AH = p) : e !== this._$AH && e !== S && this._(e) : e._$litType$ !== void 0 ? this.$(e) : e.nodeType !== void 0 ? this.T(e) : Ke(e) ? this.k(e) : this._(e);
  }
  O(e) {
    return this._$AA.parentNode.insertBefore(e, this._$AB);
  }
  T(e) {
    this._$AH !== e && (this._$AR(), this._$AH = this.O(e));
  }
  _(e) {
    this._$AH !== p && q(this._$AH) ? this._$AA.nextSibling.data = e : this.T(b.createTextNode(e)), this._$AH = e;
  }
  $(e) {
    var n;
    const { values: t, _$litType$: s } = e, r = typeof s == "number" ? this._$AC(e) : (s.el === void 0 && (s.el = z.createElement(Pe(s.h, s.h[0]), this.options)), s);
    if (((n = this._$AH) == null ? void 0 : n._$AD) === r) this._$AH.p(t);
    else {
      const o = new Ye(r, this), c = o.u(this.options);
      o.p(t), this.T(c), this._$AH = o;
    }
  }
  _$AC(e) {
    let t = ve.get(e.strings);
    return t === void 0 && ve.set(e.strings, t = new z(e)), t;
  }
  k(e) {
    re(this._$AH) || (this._$AH = [], this._$AR());
    const t = this._$AH;
    let s, r = 0;
    for (const n of e) r === t.length ? t.push(s = new D(this.O(U()), this.O(U()), this, this.options)) : s = t[r], s._$AI(n), r++;
    r < t.length && (this._$AR(s && s._$AB.nextSibling, r), t.length = r);
  }
  _$AR(e = this._$AA.nextSibling, t) {
    var s;
    for ((s = this._$AP) == null ? void 0 : s.call(this, !1, !0, t); e !== this._$AB; ) {
      const r = me(e).nextSibling;
      me(e).remove(), e = r;
    }
  }
  setConnected(e) {
    var t;
    this._$AM === void 0 && (this._$Cv = e, (t = this._$AP) == null || t.call(this, e));
  }
}
class Y {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(e, t, s, r, n) {
    this.type = 1, this._$AH = p, this._$AN = void 0, this.element = e, this.name = t, this._$AM = r, this.options = n, s.length > 2 || s[0] !== "" || s[1] !== "" ? (this._$AH = Array(s.length - 1).fill(new String()), this.strings = s) : this._$AH = p;
  }
  _$AI(e, t = this, s, r) {
    const n = this.strings;
    let o = !1;
    if (n === void 0) e = C(this, e, t, 0), o = !q(e) || e !== this._$AH && e !== S, o && (this._$AH = e);
    else {
      const c = e;
      let a, l;
      for (e = n[0], a = 0; a < n.length - 1; a++) l = C(this, c[s + a], t, a), l === S && (l = this._$AH[a]), o || (o = !q(l) || l !== this._$AH[a]), l === p ? e = p : e !== p && (e += (l ?? "") + n[a + 1]), this._$AH[a] = l;
    }
    o && !r && this.j(e);
  }
  j(e) {
    e === p ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
  }
}
class Ge extends Y {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(e) {
    this.element[this.name] = e === p ? void 0 : e;
  }
}
class Ze extends Y {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(e) {
    this.element.toggleAttribute(this.name, !!e && e !== p);
  }
}
class Je extends Y {
  constructor(e, t, s, r, n) {
    super(e, t, s, r, n), this.type = 5;
  }
  _$AI(e, t = this) {
    if ((e = C(this, e, t, 0) ?? p) === S) return;
    const s = this._$AH, r = e === p && s !== p || e.capture !== s.capture || e.once !== s.once || e.passive !== s.passive, n = e !== p && (s === p || r);
    r && this.element.removeEventListener(this.name, this, s), n && this.element.addEventListener(this.name, this, e), this._$AH = e;
  }
  handleEvent(e) {
    var t;
    typeof this._$AH == "function" ? this._$AH.call(((t = this.options) == null ? void 0 : t.host) ?? this.element, e) : this._$AH.handleEvent(e);
  }
}
class Xe {
  constructor(e, t, s) {
    this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = s;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(e) {
    C(this, e);
  }
}
const Q = N.litHtmlPolyfillSupport;
Q == null || Q(z, D), (N.litHtmlVersions ?? (N.litHtmlVersions = [])).push("3.3.3");
const Qe = (i, e, t) => {
  const s = (t == null ? void 0 : t.renderBefore) ?? e;
  let r = s._$litPart$;
  if (r === void 0) {
    const n = (t == null ? void 0 : t.renderBefore) ?? null;
    s._$litPart$ = r = new D(e.insertBefore(U(), n), n, void 0, t ?? {});
  }
  return r._$AI(i), r;
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const w = globalThis;
class E extends A {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    var t;
    const e = super.createRenderRoot();
    return (t = this.renderOptions).renderBefore ?? (t.renderBefore = e.firstChild), e;
  }
  update(e) {
    const t = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = Qe(t, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    var e;
    super.connectedCallback(), (e = this._$Do) == null || e.setConnected(!0);
  }
  disconnectedCallback() {
    var e;
    super.disconnectedCallback(), (e = this._$Do) == null || e.setConnected(!1);
  }
  render() {
    return S;
  }
}
var xe;
E._$litElement$ = !0, E.finalized = !0, (xe = w.litElementHydrateSupport) == null || xe.call(w, { LitElement: E });
const ee = w.litElementPolyfillSupport;
ee == null || ee({ LitElement: E });
(w.litElementVersions ?? (w.litElementVersions = [])).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const ke = (i) => (e, t) => {
  t !== void 0 ? t.addInitializer(() => {
    customElements.define(i, e);
  }) : customElements.define(i, e);
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const et = { attribute: !0, type: String, converter: V, reflect: !1, hasChanged: se }, tt = (i = et, e, t) => {
  const { kind: s, metadata: r } = t;
  let n = globalThis.litPropertyMetadata.get(r);
  if (n === void 0 && globalThis.litPropertyMetadata.set(r, n = /* @__PURE__ */ new Map()), s === "setter" && ((i = Object.create(i)).wrapped = !0), n.set(t.name, i), s === "accessor") {
    const { name: o } = t;
    return { set(c) {
      const a = e.get.call(this);
      e.set.call(this, c), this.requestUpdate(o, a, i, !0, c);
    }, init(c) {
      return c !== void 0 && this.C(o, void 0, i, c), c;
    } };
  }
  if (s === "setter") {
    const { name: o } = t;
    return function(c) {
      const a = this[o];
      e.call(this, c), this.requestUpdate(o, a, i, !0, c);
    };
  }
  throw Error("Unsupported decorator location: " + s);
};
function ne(i) {
  return (e, t) => typeof t == "object" ? tt(i, e, t) : ((s, r, n) => {
    const o = r.hasOwnProperty(n);
    return r.constructor.createProperty(n, s), o ? Object.getOwnPropertyDescriptor(r, n) : void 0;
  })(i, e, t);
}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
function oe(i) {
  return ne({ ...i, state: !0, attribute: !1 });
}
const it = "shuruq", st = "midnight", rt = "last_third", nt = /* @__PURE__ */ new Set([
  "calculation_method",
  "madhab",
  "high_latitude_rule",
  "night_length",
  "night_duration",
  "fajr_angle",
  "ishaa_angle",
  "ishaa_interval",
  "fajr_offset",
  "shuruq_offset",
  "dhuhr_offset",
  "asr_offset",
  "maghrib_offset",
  "ishaa_offset"
]);
function ae(i = {}) {
  const e = ["fajr"];
  return i.showShuruq && e.push(it), e.push("dhuhr", "asr", "maghrib", "ishaa"), i.showMidnight && e.push(st), i.showLastThird && e.push(rt), e;
}
function ot(i = {}) {
  return 5 + (i.showShuruq ? 1 : 0);
}
function at(i, e = {}) {
  return nt.has(i) ? !1 : ae(e).includes(i);
}
function we(i, e = {}) {
  const s = ae(e).indexOf(i);
  return s === -1 ? 999 : s;
}
const lt = "mawaqeet", ct = "mdi:mosque", ht = {
  fajr: "mdi:weather-sunset-up",
  shuruq: "mdi:weather-sunny",
  dhuhr: "mdi:white-balance-sunny",
  asr: "mdi:weather-partly-cloudy",
  maghrib: "mdi:weather-sunset",
  ishaa: "mdi:weather-night",
  midnight: "mdi:clock-time-twelve",
  last_third: "mdi:clock-outline"
};
function dt(i, e, t) {
  const s = t == null ? void 0 : t[i];
  return s || e || ht[i] || ct;
}
function ut(i) {
  var t;
  return i.translation_key ? i.translation_key : ((t = i.entity_id.split(".").pop()) == null ? void 0 : t.split("_").pop()) ?? null;
}
function pt(i, e, t = {}, s) {
  if (!e || !i.entities)
    return [];
  const r = ae(t), n = [];
  for (const a of Object.values(i.entities)) {
    if (a.platform !== lt || a.device_id !== e || !a.entity_id.startsWith("sensor."))
      continue;
    const l = ut(a);
    if (!l || !at(l, t))
      continue;
    const d = i.states[a.entity_id];
    if (!d || d.state === "unavailable" || d.state === "unknown")
      continue;
    const h = d.attributes.device_class;
    if (h && h !== "timestamp")
      continue;
    const u = new Date(d.state);
    Number.isNaN(u.getTime()) || n.push({
      entity_id: a.entity_id,
      prayer_key: l,
      label: mt(i, a, d),
      icon: dt(
        l,
        d.attributes.icon,
        s
      ),
      at: u,
      state: d
    });
  }
  n.sort(
    (a, l) => we(a.prayer_key, t) - we(l.prayer_key, t)
  );
  const o = ot(t);
  return n.filter(
    (a) => r.filter((l) => l !== "midnight" && l !== "last_third").includes(a.prayer_key)
  ).length < o ? [] : n;
}
function H(i, e = /* @__PURE__ */ new Date()) {
  if (i.length === 0)
    return null;
  const t = i.filter((n) => n.at.getTime() > e.getTime());
  if (t.length > 0)
    return {
      prayer: t[0],
      following: t[1] ?? null,
      isTomorrow: !1
    };
  const s = i.find((n) => n.prayer_key === "fajr") ?? i[0], r = i.find((n) => n.prayer_key !== s.prayer_key) ?? null;
  return {
    prayer: s,
    following: r,
    isTomorrow: !0
  };
}
function mt(i, e, t) {
  var s;
  if (e.translation_key) {
    const r = `component.mawaqeet.entity.sensor.${e.translation_key}.name`, n = (s = i.localize) == null ? void 0 : s.call(i, r);
    if (n && n !== r)
      return n;
  }
  return t.attributes.friendly_name || e.entity_id;
}
function P(i, e, t) {
  var r, n;
  const s = t === "12" || t === "system" && ((r = e.locale) == null ? void 0 : r.time_format) === "12";
  return new Intl.DateTimeFormat(((n = e.locale) == null ? void 0 : n.language) || void 0, {
    hour: "numeric",
    minute: "2-digit",
    hour12: s
  }).format(i);
}
function le(i, e = /* @__PURE__ */ new Date(), t = !1) {
  const s = i.getTime() - e.getTime();
  if (t && s < 0) {
    const r = new Date(i);
    return r.setDate(r.getDate() + 1), be(r.getTime() - e.getTime());
  }
  return be(s);
}
function be(i) {
  const e = Math.abs(i), t = Math.round(e / 6e4);
  if (t < 1)
    return i >= 0 ? "now" : "just now";
  if (t < 60)
    return i >= 0 ? `in ${t}m` : `${t}m ago`;
  const s = Math.floor(t / 60), r = t % 60;
  if (s < 24) {
    const o = r > 0 ? `${s}h ${r}m` : `${s}h`;
    return i >= 0 ? `in ${o}` : `${o} ago`;
  }
  const n = Math.floor(s / 24);
  return i >= 0 ? `in ${n}d` : `${n}d ago`;
}
function ft(i, e) {
  var s;
  const t = (s = i.devices) == null ? void 0 : s[e];
  return t ? t.name_by_user || t.name || e : "";
}
function _t(i) {
  switch (i) {
    case "horizontal":
    case "combined":
      return {
        columns: 12,
        rows: "auto",
        min_rows: 2,
        min_columns: 6
      };
    case "timeline":
      return {
        columns: 12,
        rows: 3,
        min_rows: 3,
        max_rows: 4
      };
    case "vertical":
    case "agenda":
      return {
        columns: 6,
        rows: "auto",
        min_rows: 4,
        min_columns: 3
      };
    case "next":
    default:
      return {
        columns: 6,
        rows: 2,
        min_rows: 2,
        min_columns: 3
      };
  }
}
function R(i, e) {
  return e.time_format ?? "system";
}
function L(i, e) {
  if (!e.show_device_name || !e.device)
    return p;
  const t = ft(i, e.device);
  return t ? m`<div class="header">${t}</div>` : p;
}
function W(i) {
  return m`<div class="error">${i}</div>`;
}
function j(i) {
  return m`<span class="icon-slot" aria-hidden="true"
    ><ha-icon .icon=${i}></ha-icon
  ></span>`;
}
function Te(i, e) {
  return (t) => {
    t.stopPropagation(), e(i);
  };
}
function Oe(i, e) {
  return (t) => {
    (t.key === "Enter" || t.key === " ") && (t.preventDefault(), t.stopPropagation(), e(i));
  };
}
function G(i, e, t, s, r) {
  return m`
    <div
      class=${t}
      @click=${Te(i, e)}
      @keydown=${Oe(i, e)}
      role="button"
      tabindex="0"
      aria-label=${r ?? p}
    >
      ${s}
    </div>
  `;
}
function Me(i, e, t, s, r) {
  const n = H(t, s);
  if (!n)
    return W("No prayer times available.");
  const { prayer: o, following: c, isTomorrow: a } = n, l = R(i, e), d = le(o.at, s, a), h = P(o.at, i, l), u = c && m`Following: ${c.label} at ${P(c.at, i, l)}`, f = `Next prayer: ${o.label} ${d} at ${h}`;
  return m`
    ${L(i, e)}
    ${G(
    o.entity_id,
    r,
    "next-hero",
    m`
        ${j(o.icon)}
        <div class="prayer-name">${o.label}</div>
        <div class="countdown">${d}</div>
        <div class="at-time">${h}</div>
        ${a ? m`<div class="tomorrow-badge">Tomorrow</div>` : p}
        ${u ? m`<div class="following">${u}</div>` : p}
      `,
    f
  )}
  `;
}
function $t(i, e, t, s, r) {
  const n = H(t, s), o = n == null ? void 0 : n.prayer.entity_id, c = R(i, e), a = e.show_relative !== !1;
  return m`
    ${L(i, e)}
    ${t.map((l) => {
    const d = l.entity_id === o, h = e.show_passed_style !== !1 && l.at.getTime() < s.getTime(), u = ["row", d ? "next" : "", h ? "passed" : ""].filter(Boolean).join(" "), f = P(l.at, i, c);
    return G(
      l.entity_id,
      r,
      u,
      m`
          ${j(l.icon)}
          <span class="name">${l.label}</span>
          <span class="times">
            <div>${f}</div>
            ${a ? m`<div class="relative">
                  ${le(l.at, s)}
                </div>` : p}
          </span>
        `,
      `${l.label} ${f}`
    );
  })}
  `;
}
function Ne(i, e, t, s, r) {
  const n = H(t, s), o = n == null ? void 0 : n.prayer.entity_id, c = R(i, e), a = e.show_relative === !0;
  return m`
    ${L(i, e)}
    <div class="horizontal">
      ${t.map((l) => {
    const d = l.entity_id === o, h = e.show_passed_style !== !1 && l.at.getTime() < s.getTime(), u = ["chip", d ? "next" : "", h ? "passed" : ""].filter(Boolean).join(" "), f = P(l.at, i, c);
    return G(
      l.entity_id,
      r,
      u,
      m`
            ${j(l.icon)}
            <div>${l.label}</div>
            <div class="chip-time">${f}</div>
            ${a ? m`<div class="chip-relative">
                  ${le(l.at, s)}
                </div>` : p}
          `,
      `${l.label} ${f}`
    );
  })}
    </div>
  `;
}
function gt(i, e, t, s, r) {
  return m`
    ${Me(i, { ...e, show_device_name: !1 }, t, s, r)}
    <hr class="divider" />
    ${Ne(
    i,
    { ...e, show_device_name: !1, show_relative: !1 },
    t,
    s,
    r
  )}
  `;
}
function yt(i, e, t, s, r) {
  const n = H(t, s), o = n == null ? void 0 : n.prayer.entity_id, c = t.filter((h) => h.at.getTime() > s.getTime()), a = t.filter((h) => h.at.getTime() <= s.getTime()), l = R(i, e), d = (h, u) => m`
    <div class="section-title">${h}</div>
    ${u.map((f) => {
    const _ = f.entity_id === o, I = a.includes(f), Z = ["row", _ ? "next" : "", I ? "passed" : ""].filter(Boolean).join(" "), T = P(f.at, i, l);
    return G(
      f.entity_id,
      r,
      Z,
      m`
          <span class="agenda-status" aria-hidden="true">
            ${I ? m`<ha-icon .icon=${"mdi:check"}></ha-icon>` : p}
          </span>
          ${j(f.icon)}
          <span class="name">${f.label}</span>
          <span class="times">${T}</span>
        `,
      `${f.label} ${T}`
    );
  })}
  `;
  return m`
    ${L(i, e)}
    ${a.length ? d("Earlier today", a) : p}
    ${c.length ? d("Upcoming", c) : m`<div class="section-title">Upcoming</div>
          <div class="agenda-empty">All prayers complete for today</div>`}
  `;
}
function vt(i, e, t, s, r) {
  if (t.length < 2)
    return W("Not enough prayer times for timeline.");
  const n = t[0].at.getTime(), c = t[t.length - 1].at.getTime() - n || 1, a = Math.min(
    100,
    Math.max(0, (s.getTime() - n) / c * 100)
  ), l = R(i, e), d = H(t, s), h = d == null ? void 0 : d.prayer.entity_id;
  return m`
    ${L(i, e)}
    <div class="timeline">
      <div class="timeline-track"></div>
      <div class="timeline-now" style="left: ${a}%"></div>
      ${t.map((u) => {
    const f = (u.at.getTime() - n) / c * 100, _ = u.entity_id === h, I = e.show_passed_style !== !1 && u.at.getTime() < s.getTime(), Z = [
      "timeline-marker",
      _ ? "next" : "",
      I ? "passed" : ""
    ].filter(Boolean).join(" "), T = P(u.at, i, l), ce = `${u.label} ${T}`;
    return m`
          <div
            class=${Z}
            style="left: ${f}%"
            @click=${Te(u.entity_id, r)}
            @keydown=${Oe(u.entity_id, r)}
            role="button"
            tabindex="0"
            aria-label=${ce}
            title=${ce}
          >
            ${j(u.icon)}
            <div>${u.label}</div>
            <div>${T}</div>
          </div>
        `;
  })}
    </div>
  `;
}
function wt(i, e, t, s, r) {
  switch (e.layout ?? "next") {
    case "horizontal":
      return Ne(i, e, t, s, r);
    case "vertical":
      return $t(i, e, t, s, r);
    case "combined":
      return gt(i, e, t, s, r);
    case "timeline":
      return vt(i, e, t, s, r);
    case "agenda":
      return yt(i, e, t, s, r);
  }
  return Me(i, e, t, s, r);
}
const bt = qe`
  :host {
    display: block;
    height: 100%;
  }

  ha-card {
    height: 100%;
    overflow: hidden;
    padding: 16px;
    display: flex;
    flex-direction: column;
  }

  .header {
    font-size: 0.85em;
    opacity: 0.7;
    margin-bottom: 8px;
  }

  .error {
    color: var(--error-color, #b71c1c);
    padding: 8px 0;
  }

  .icon-slot {
    width: 24px;
    flex-shrink: 0;
    display: grid;
    place-items: center;
  }

  .row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 4px;
    border-radius: 8px;
    cursor: pointer;
  }

  .row:hover {
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.05));
  }

  .row.next {
    font-weight: 600;
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
    box-shadow: inset 3px 0 0 var(--primary-color);
  }

  .row.passed,
  .chip.passed,
  .timeline-marker.passed {
    opacity: 0.6;
    color: var(--secondary-text-color);
  }

  .row.passed ha-icon,
  .chip.passed ha-icon,
  .timeline-marker.passed ha-icon {
    color: var(--secondary-text-color);
  }

  .row ha-icon,
  .chip ha-icon {
    --mdc-icon-size: 22px;
    color: var(--primary-color);
  }

  .row .name {
    flex: 1;
    min-width: 0;
  }

  .row .times {
    text-align: end;
    white-space: nowrap;
  }

  .row .relative {
    font-size: 0.75em;
    opacity: 0.7;
  }

  .next-hero {
    text-align: center;
    padding: 8px 0 16px;
    cursor: pointer;
  }

  .next-hero .icon-slot {
    width: auto;
    margin: 0 auto;
  }

  .next-hero ha-icon {
    --mdc-icon-size: 40px;
    color: var(--primary-color);
  }

  .next-hero .prayer-name {
    font-size: 1.5em;
    font-weight: 600;
    margin: 8px 0 4px;
  }

  .next-hero .countdown {
    font-size: 1.35em;
    color: var(--primary-color);
    font-weight: 600;
  }

  .next-hero .at-time {
    font-size: 0.95em;
    opacity: 0.75;
    margin-top: 2px;
  }

  .next-hero .tomorrow-badge {
    display: inline-block;
    margin-top: 8px;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75em;
    font-weight: 600;
    color: var(--primary-color);
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
  }

  .next-hero .following {
    font-size: 0.85em;
    opacity: 0.7;
    margin-top: 8px;
  }

  .horizontal {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    align-items: stretch;
  }

  .chip {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 8px;
    border-radius: 8px;
    min-width: 4.5em;
    border: 1px solid transparent;
    cursor: pointer;
    gap: 2px;
  }

  .chip.next {
    border-color: var(--primary-color);
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
    font-weight: 600;
  }

  .chip .chip-time {
    font-size: 0.95em;
    margin-top: 2px;
  }

  .chip .chip-relative {
    font-size: 0.7em;
    opacity: 0.7;
  }

  .divider {
    border: none;
    border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
    margin: 12px 0;
  }

  .section-title {
    font-size: 0.75em;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    opacity: 0.6;
    margin: 12px 0 6px;
  }

  .agenda-empty {
    font-size: 0.9em;
    opacity: 0.65;
    padding: 4px 0 8px;
  }

  .agenda-status {
    width: 20px;
    flex-shrink: 0;
    display: grid;
    place-items: center;
    color: var(--secondary-text-color);
  }

  .agenda-status ha-icon {
    --mdc-icon-size: 18px;
    color: var(--secondary-text-color);
  }

  .timeline {
    position: relative;
    height: 80px;
    margin: 28px 12px 36px;
  }

  .timeline-track {
    position: absolute;
    left: 0;
    right: 0;
    top: 50%;
    height: 4px;
    background: var(--divider-color, rgba(0, 0, 0, 0.15));
    border-radius: 2px;
    transform: translateY(-50%);
  }

  .timeline-marker {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    text-align: center;
    font-size: 0.72em;
    white-space: nowrap;
    cursor: pointer;
  }

  .timeline-marker .icon-slot {
    width: auto;
    margin: 0 auto;
  }

  .timeline-marker ha-icon {
    --mdc-icon-size: 18px;
    color: var(--primary-color);
  }

  .timeline-marker.next {
    font-weight: 600;
  }

  .timeline-marker.next ha-icon {
    --mdc-icon-size: 20px;
  }

  .timeline-now {
    position: absolute;
    top: -4px;
    width: 2px;
    height: 88px;
    background: var(--accent-color, var(--primary-color));
    transform: translateX(-50%);
    z-index: 1;
  }
`;
var xt = Object.defineProperty, At = Object.getOwnPropertyDescriptor, x = (i, e, t, s) => {
  for (var r = s > 1 ? void 0 : s ? At(e, t) : e, n = i.length - 1, o; n >= 0; n--)
    (o = i[n]) && (r = (s ? o(e, t, r) : o(r)) || r);
  return s && r && xt(e, t, r), r;
};
let k = class extends E {
  constructor() {
    super(...arguments), this._now = /* @__PURE__ */ new Date();
  }
  setConfig(i) {
    if (!i.device)
      throw new Error("Set a Mawaqeet device for this card.");
    this._config = {
      type: "custom:mawaqeet-prayer-card",
      layout: "next",
      show_shuruq: !1,
      show_midnight: !1,
      show_last_third: !1,
      show_passed_style: !0,
      time_format: "system",
      show_relative: !0,
      show_device_name: !1,
      ...i
    };
  }
  getCardSize() {
    var e;
    switch (((e = this._config) == null ? void 0 : e.layout) ?? "next") {
      case "horizontal":
      case "combined":
        return 2;
      case "vertical":
      case "agenda":
        return 4;
      case "timeline":
        return 3;
      default:
        return 2;
    }
  }
  getGridOptions() {
    var e;
    const i = ((e = this._config) == null ? void 0 : e.layout) ?? "next";
    return _t(i);
  }
  static async getConfigElement() {
    return document.createElement("mawaqeet-prayer-card-editor");
  }
  static getStubConfig() {
    return {
      type: "custom:mawaqeet-prayer-card",
      layout: "next",
      show_shuruq: !1,
      show_midnight: !1,
      show_last_third: !1
    };
  }
  connectedCallback() {
    super.connectedCallback(), this._clockInterval = window.setInterval(() => {
      this._now = /* @__PURE__ */ new Date();
    }, 6e4);
  }
  disconnectedCallback() {
    super.disconnectedCallback(), this._clockInterval !== void 0 && window.clearInterval(this._clockInterval);
  }
  willUpdate(i) {
    i.has("hass") && (this._now = /* @__PURE__ */ new Date());
  }
  render() {
    if (!this.hass || !this._config)
      return m`<ha-card><div class="error">Loading…</div></ha-card>`;
    const i = {
      showShuruq: this._config.show_shuruq === !0,
      showMidnight: this._config.show_midnight === !0,
      showLastThird: this._config.show_last_third === !0
    }, e = pt(
      this.hass,
      this._config.device,
      i,
      this._config.icons
    );
    let t;
    return this._config.device ? e.length === 0 ? t = W(
      "No prayer times found for this device. Check that Mawaqeet is loaded."
    ) : t = wt(
      this.hass,
      this._config,
      e,
      this._now,
      (s) => this._moreInfo(s)
    ) : t = W("Select a Mawaqeet location device in card settings."), m`<ha-card>${t}</ha-card>`;
  }
  _moreInfo(i) {
    const e = new CustomEvent("hass-more-info", {
      bubbles: !0,
      composed: !0,
      detail: { entityId: i }
    });
    this.dispatchEvent(e);
  }
};
k.styles = bt;
x([
  ne({ attribute: !1 })
], k.prototype, "hass", 2);
x([
  oe()
], k.prototype, "_config", 2);
x([
  oe()
], k.prototype, "_now", 2);
k = x([
  ke("mawaqeet-prayer-card")
], k);
function Et(i) {
  const e = [
    { name: "fajr", selector: { icon: {} } }
  ];
  return i.show_shuruq && e.push({ name: "shuruq", selector: { icon: {} } }), e.push(
    { name: "dhuhr", selector: { icon: {} } },
    { name: "asr", selector: { icon: {} } },
    { name: "maghrib", selector: { icon: {} } },
    { name: "ishaa", selector: { icon: {} } }
  ), i.show_midnight && e.push({ name: "midnight", selector: { icon: {} } }), i.show_last_third && e.push({ name: "last_third", selector: { icon: {} } }), [
    {
      name: "device",
      required: !0,
      selector: {
        device: { filter: { integration: "mawaqeet" } }
      }
    },
    {
      name: "layout",
      selector: {
        select: {
          options: [
            { value: "next", label: "Next prayer" },
            { value: "horizontal", label: "Horizontal timetable" },
            { value: "vertical", label: "Vertical timetable" },
            { value: "combined", label: "Combined (next + horizontal)" },
            { value: "timeline", label: "Day timeline" },
            { value: "agenda", label: "Agenda" }
          ]
        }
      }
    },
    { name: "show_shuruq", selector: { boolean: {} } },
    { name: "show_midnight", selector: { boolean: {} } },
    { name: "show_last_third", selector: { boolean: {} } },
    { name: "show_passed_style", selector: { boolean: {} } },
    {
      name: "time_format",
      selector: {
        select: {
          options: [
            { value: "system", label: "System" },
            { value: "24", label: "24-hour" },
            { value: "12", label: "12-hour" }
          ]
        }
      }
    },
    { name: "show_relative", selector: { boolean: {} } },
    { name: "show_device_name", selector: { boolean: {} } },
    {
      name: "icons",
      type: "expandable",
      title: "Custom prayer icons",
      schema: e,
      expanded: !1
    }
  ];
}
function St(i) {
  if (!i)
    return;
  const e = {};
  for (const [t, s] of Object.entries(i))
    typeof s == "string" && s.trim() && (e[t] = s.trim());
  return Object.keys(e).length ? e : void 0;
}
let F = class extends E {
  setConfig(i) {
    this._config = i;
  }
  render() {
    return !this.hass || !this._config ? m`` : m`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${Et(this._config)}
        .computeLabel=${(i) => Ct[i.name] ?? i.name}
        @value-changed=${this._changed}
      ></ha-form>
    `;
  }
  _changed(i) {
    i.stopPropagation();
    const e = i.detail.value, t = St(e.icons), s = { ...e };
    t ? s.icons = t : delete s.icons, this._config = s;
    const r = new CustomEvent("config-changed", {
      detail: { config: s },
      bubbles: !0,
      composed: !0
    });
    this.dispatchEvent(r);
  }
};
x([
  ne({ attribute: !1 })
], F.prototype, "hass", 2);
x([
  oe()
], F.prototype, "_config", 2);
F = x([
  ke("mawaqeet-prayer-card-editor")
], F);
const Ct = {
  device: "Mawaqeet location",
  layout: "Layout",
  show_shuruq: "Show Shuruq (sunrise)",
  show_midnight: "Show Midnight",
  show_last_third: "Show Last Third",
  show_passed_style: "Dim passed prayers",
  time_format: "Time format",
  show_relative: "Show relative times",
  show_device_name: "Show location name",
  icons: "Custom prayer icons",
  fajr: "Fajr",
  shuruq: "Shuruq",
  dhuhr: "Dhuhr",
  asr: "Asr",
  maghrib: "Maghrib",
  ishaa: "Ishaa",
  midnight: "Midnight",
  last_third: "Last Third"
};
typeof window < "u" && (window.customCards = window.customCards || [], window.customCards.push({
  type: "mawaqeet-prayer-card",
  name: "Mawaqeet Prayer",
  description: "Prayer times from a Mawaqeet location device",
  preview: !0
}));
export {
  k as MawaqeetPrayerCard,
  F as MawaqeetPrayerCardEditor
};
