/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const I = globalThis, J = I.ShadowRoot && (I.ShadyCSS === void 0 || I.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, Q = Symbol(), oe = /* @__PURE__ */ new WeakMap();
let ye = class {
  constructor(e, t, i) {
    if (this._$cssResult$ = !0, i !== Q) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = e, this.t = t;
  }
  get styleSheet() {
    let e = this.o;
    const t = this.t;
    if (J && e === void 0) {
      const i = t !== void 0 && t.length === 1;
      i && (e = oe.get(t)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), i && oe.set(t, e));
    }
    return e;
  }
  toString() {
    return this.cssText;
  }
};
const Oe = (s) => new ye(typeof s == "string" ? s : s + "", void 0, Q), ke = (s, ...e) => {
  const t = s.length === 1 ? s[0] : e.reduce((i, r, n) => i + ((o) => {
    if (o._$cssResult$ === !0) return o.cssText;
    if (typeof o == "number") return o;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + o + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(r) + s[n + 1], s[0]);
  return new ye(t, s, Q);
}, Ue = (s, e) => {
  if (J) s.adoptedStyleSheets = e.map((t) => t instanceof CSSStyleSheet ? t : t.styleSheet);
  else for (const t of e) {
    const i = document.createElement("style"), r = I.litNonce;
    r !== void 0 && i.setAttribute("nonce", r), i.textContent = t.cssText, s.appendChild(i);
  }
}, ae = J ? (s) => s : (s) => s instanceof CSSStyleSheet ? ((e) => {
  let t = "";
  for (const i of e.cssRules) t += i.cssText;
  return Oe(t);
})(s) : s;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const { is: Ne, defineProperty: Me, getOwnPropertyDescriptor: Re, getOwnPropertyNames: ze, getOwnPropertySymbols: De, getPrototypeOf: He } = Object, $ = globalThis, le = $.trustedTypes, qe = le ? le.emptyScript : "", F = $.reactiveElementPolyfillSupport, k = (s, e) => s, L = { toAttribute(s, e) {
  switch (e) {
    case Boolean:
      s = s ? qe : null;
      break;
    case Object:
    case Array:
      s = s == null ? s : JSON.stringify(s);
  }
  return s;
}, fromAttribute(s, e) {
  let t = s;
  switch (e) {
    case Boolean:
      t = s !== null;
      break;
    case Number:
      t = s === null ? null : Number(s);
      break;
    case Object:
    case Array:
      try {
        t = JSON.parse(s);
      } catch {
        t = null;
      }
  }
  return t;
} }, ee = (s, e) => !Ne(s, e), ce = { attribute: !0, type: String, converter: L, reflect: !1, useDefault: !1, hasChanged: ee };
Symbol.metadata ?? (Symbol.metadata = Symbol("metadata")), $.litPropertyMetadata ?? ($.litPropertyMetadata = /* @__PURE__ */ new WeakMap());
let x = class extends HTMLElement {
  static addInitializer(e) {
    this._$Ei(), (this.l ?? (this.l = [])).push(e);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(e, t = ce) {
    if (t.state && (t.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(e) && ((t = Object.create(t)).wrapped = !0), this.elementProperties.set(e, t), !t.noAccessor) {
      const i = Symbol(), r = this.getPropertyDescriptor(e, i, t);
      r !== void 0 && Me(this.prototype, e, r);
    }
  }
  static getPropertyDescriptor(e, t, i) {
    const { get: r, set: n } = Re(this.prototype, e) ?? { get() {
      return this[t];
    }, set(o) {
      this[t] = o;
    } };
    return { get: r, set(o) {
      const a = r == null ? void 0 : r.call(this);
      n == null || n.call(this, o), this.requestUpdate(e, a, i);
    }, configurable: !0, enumerable: !0 };
  }
  static getPropertyOptions(e) {
    return this.elementProperties.get(e) ?? ce;
  }
  static _$Ei() {
    if (this.hasOwnProperty(k("elementProperties"))) return;
    const e = He(this);
    e.finalize(), e.l !== void 0 && (this.l = [...e.l]), this.elementProperties = new Map(e.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(k("finalized"))) return;
    if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(k("properties"))) {
      const t = this.properties, i = [...ze(t), ...De(t)];
      for (const r of i) this.createProperty(r, t[r]);
    }
    const e = this[Symbol.metadata];
    if (e !== null) {
      const t = litPropertyMetadata.get(e);
      if (t !== void 0) for (const [i, r] of t) this.elementProperties.set(i, r);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [t, i] of this.elementProperties) {
      const r = this._$Eu(t, i);
      r !== void 0 && this._$Eh.set(r, t);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(e) {
    const t = [];
    if (Array.isArray(e)) {
      const i = new Set(e.flat(1 / 0).reverse());
      for (const r of i) t.unshift(ae(r));
    } else e !== void 0 && t.push(ae(e));
    return t;
  }
  static _$Eu(e, t) {
    const i = t.attribute;
    return i === !1 ? void 0 : typeof i == "string" ? i : typeof e == "string" ? e.toLowerCase() : void 0;
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
    for (const i of t.keys()) this.hasOwnProperty(i) && (e.set(i, this[i]), delete this[i]);
    e.size > 0 && (this._$Ep = e);
  }
  createRenderRoot() {
    const e = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return Ue(e, this.constructor.elementStyles), e;
  }
  connectedCallback() {
    var e;
    this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this.enableUpdating(!0), (e = this._$EO) == null || e.forEach((t) => {
      var i;
      return (i = t.hostConnected) == null ? void 0 : i.call(t);
    });
  }
  enableUpdating(e) {
  }
  disconnectedCallback() {
    var e;
    (e = this._$EO) == null || e.forEach((t) => {
      var i;
      return (i = t.hostDisconnected) == null ? void 0 : i.call(t);
    });
  }
  attributeChangedCallback(e, t, i) {
    this._$AK(e, i);
  }
  _$ET(e, t) {
    var n;
    const i = this.constructor.elementProperties.get(e), r = this.constructor._$Eu(e, i);
    if (r !== void 0 && i.reflect === !0) {
      const o = (((n = i.converter) == null ? void 0 : n.toAttribute) !== void 0 ? i.converter : L).toAttribute(t, i.type);
      this._$Em = e, o == null ? this.removeAttribute(r) : this.setAttribute(r, o), this._$Em = null;
    }
  }
  _$AK(e, t) {
    var n, o;
    const i = this.constructor, r = i._$Eh.get(e);
    if (r !== void 0 && this._$Em !== r) {
      const a = i.getPropertyOptions(r), l = typeof a.converter == "function" ? { fromAttribute: a.converter } : ((n = a.converter) == null ? void 0 : n.fromAttribute) !== void 0 ? a.converter : L;
      this._$Em = r;
      const c = l.fromAttribute(t, a.type);
      this[r] = c ?? ((o = this._$Ej) == null ? void 0 : o.get(r)) ?? c, this._$Em = null;
    }
  }
  requestUpdate(e, t, i, r = !1, n) {
    var o;
    if (e !== void 0) {
      const a = this.constructor;
      if (r === !1 && (n = this[e]), i ?? (i = a.getPropertyOptions(e)), !((i.hasChanged ?? ee)(n, t) || i.useDefault && i.reflect && n === ((o = this._$Ej) == null ? void 0 : o.get(e)) && !this.hasAttribute(a._$Eu(e, i)))) return;
      this.C(e, t, i);
    }
    this.isUpdatePending === !1 && (this._$ES = this._$EP());
  }
  C(e, t, { useDefault: i, reflect: r, wrapped: n }, o) {
    i && !(this._$Ej ?? (this._$Ej = /* @__PURE__ */ new Map())).has(e) && (this._$Ej.set(e, o ?? t ?? this[e]), n !== !0 || o !== void 0) || (this._$AL.has(e) || (this.hasUpdated || i || (t = void 0), this._$AL.set(e, t)), r === !0 && this._$Em !== e && (this._$Eq ?? (this._$Eq = /* @__PURE__ */ new Set())).add(e));
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
    var i;
    if (!this.isUpdatePending) return;
    if (!this.hasUpdated) {
      if (this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this._$Ep) {
        for (const [n, o] of this._$Ep) this[n] = o;
        this._$Ep = void 0;
      }
      const r = this.constructor.elementProperties;
      if (r.size > 0) for (const [n, o] of r) {
        const { wrapped: a } = o, l = this[n];
        a !== !0 || this._$AL.has(n) || l === void 0 || this.C(n, void 0, o, l);
      }
    }
    let e = !1;
    const t = this._$AL;
    try {
      e = this.shouldUpdate(t), e ? (this.willUpdate(t), (i = this._$EO) == null || i.forEach((r) => {
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
    (t = this._$EO) == null || t.forEach((i) => {
      var r;
      return (r = i.hostUpdated) == null ? void 0 : r.call(i);
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
x.elementStyles = [], x.shadowRootOptions = { mode: "open" }, x[k("elementProperties")] = /* @__PURE__ */ new Map(), x[k("finalized")] = /* @__PURE__ */ new Map(), F == null || F({ ReactiveElement: x }), ($.reactiveElementVersions ?? ($.reactiveElementVersions = [])).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const U = globalThis, he = (s) => s, B = U.trustedTypes, de = B ? B.createPolicy("lit-html", { createHTML: (s) => s }) : void 0, we = "$lit$", _ = `lit$${Math.random().toFixed(9).slice(2)}$`, be = "?" + _, je = `<${be}>`, w = document, N = () => w.createComment(""), M = (s) => s === null || typeof s != "object" && typeof s != "function", te = Array.isArray, Ie = (s) => te(s) || typeof (s == null ? void 0 : s[Symbol.iterator]) == "function", X = `[ 	
\f\r]`, O = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, ue = /-->/g, pe = />/g, v = RegExp(`>|${X}(?:([^\\s"'>=/]+)(${X}*=${X}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g"), me = /'/g, fe = /"/g, Ae = /^(?:script|style|textarea|title)$/i, Le = (s) => (e, ...t) => ({ _$litType$: s, strings: e, values: t }), p = Le(1), S = Symbol.for("lit-noChange"), u = Symbol.for("lit-nothing"), _e = /* @__PURE__ */ new WeakMap(), g = w.createTreeWalker(w, 129);
function xe(s, e) {
  if (!te(s) || !s.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return de !== void 0 ? de.createHTML(e) : e;
}
const Be = (s, e) => {
  const t = s.length - 1, i = [];
  let r, n = e === 2 ? "<svg>" : e === 3 ? "<math>" : "", o = O;
  for (let a = 0; a < t; a++) {
    const l = s[a];
    let c, d, h = -1, m = 0;
    for (; m < l.length && (o.lastIndex = m, d = o.exec(l), d !== null); ) m = o.lastIndex, o === O ? d[1] === "!--" ? o = ue : d[1] !== void 0 ? o = pe : d[2] !== void 0 ? (Ae.test(d[2]) && (r = RegExp("</" + d[2], "g")), o = v) : d[3] !== void 0 && (o = v) : o === v ? d[0] === ">" ? (o = r ?? O, h = -1) : d[1] === void 0 ? h = -2 : (h = o.lastIndex - d[2].length, c = d[1], o = d[3] === void 0 ? v : d[3] === '"' ? fe : me) : o === fe || o === me ? o = v : o === ue || o === pe ? o = O : (o = v, r = void 0);
    const f = o === v && s[a + 1].startsWith("/>") ? " " : "";
    n += o === O ? l + je : h >= 0 ? (i.push(c), l.slice(0, h) + we + l.slice(h) + _ + f) : l + _ + (h === -2 ? a : f);
  }
  return [xe(s, n + (s[t] || "<?>") + (e === 2 ? "</svg>" : e === 3 ? "</math>" : "")), i];
};
class R {
  constructor({ strings: e, _$litType$: t }, i) {
    let r;
    this.parts = [];
    let n = 0, o = 0;
    const a = e.length - 1, l = this.parts, [c, d] = Be(e, t);
    if (this.el = R.createElement(c, i), g.currentNode = this.el.content, t === 2 || t === 3) {
      const h = this.el.content.firstChild;
      h.replaceWith(...h.childNodes);
    }
    for (; (r = g.nextNode()) !== null && l.length < a; ) {
      if (r.nodeType === 1) {
        if (r.hasAttributes()) for (const h of r.getAttributeNames()) if (h.endsWith(we)) {
          const m = d[o++], f = r.getAttribute(h).split(_), A = /([.?@])?(.*)/.exec(m);
          l.push({ type: 1, index: n, name: A[2], strings: f, ctor: A[1] === "." ? We : A[1] === "?" ? Ke : A[1] === "@" ? Ye : K }), r.removeAttribute(h);
        } else h.startsWith(_) && (l.push({ type: 6, index: n }), r.removeAttribute(h));
        if (Ae.test(r.tagName)) {
          const h = r.textContent.split(_), m = h.length - 1;
          if (m > 0) {
            r.textContent = B ? B.emptyScript : "";
            for (let f = 0; f < m; f++) r.append(h[f], N()), g.nextNode(), l.push({ type: 2, index: ++n });
            r.append(h[m], N());
          }
        }
      } else if (r.nodeType === 8) if (r.data === be) l.push({ type: 2, index: n });
      else {
        let h = -1;
        for (; (h = r.data.indexOf(_, h + 1)) !== -1; ) l.push({ type: 7, index: n }), h += _.length - 1;
      }
      n++;
    }
  }
  static createElement(e, t) {
    const i = w.createElement("template");
    return i.innerHTML = e, i;
  }
}
function C(s, e, t = s, i) {
  var o, a;
  if (e === S) return e;
  let r = i !== void 0 ? (o = t._$Co) == null ? void 0 : o[i] : t._$Cl;
  const n = M(e) ? void 0 : e._$litDirective$;
  return (r == null ? void 0 : r.constructor) !== n && ((a = r == null ? void 0 : r._$AO) == null || a.call(r, !1), n === void 0 ? r = void 0 : (r = new n(s), r._$AT(s, t, i)), i !== void 0 ? (t._$Co ?? (t._$Co = []))[i] = r : t._$Cl = r), r !== void 0 && (e = C(s, r._$AS(s, e.values), r, i)), e;
}
class Ve {
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
    const { el: { content: t }, parts: i } = this._$AD, r = ((e == null ? void 0 : e.creationScope) ?? w).importNode(t, !0);
    g.currentNode = r;
    let n = g.nextNode(), o = 0, a = 0, l = i[0];
    for (; l !== void 0; ) {
      if (o === l.index) {
        let c;
        l.type === 2 ? c = new z(n, n.nextSibling, this, e) : l.type === 1 ? c = new l.ctor(n, l.name, l.strings, this, e) : l.type === 6 && (c = new Fe(n, this, e)), this._$AV.push(c), l = i[++a];
      }
      o !== (l == null ? void 0 : l.index) && (n = g.nextNode(), o++);
    }
    return g.currentNode = w, r;
  }
  p(e) {
    let t = 0;
    for (const i of this._$AV) i !== void 0 && (i.strings !== void 0 ? (i._$AI(e, i, t), t += i.strings.length - 2) : i._$AI(e[t])), t++;
  }
}
class z {
  get _$AU() {
    var e;
    return ((e = this._$AM) == null ? void 0 : e._$AU) ?? this._$Cv;
  }
  constructor(e, t, i, r) {
    this.type = 2, this._$AH = u, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = i, this.options = r, this._$Cv = (r == null ? void 0 : r.isConnected) ?? !0;
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
    e = C(this, e, t), M(e) ? e === u || e == null || e === "" ? (this._$AH !== u && this._$AR(), this._$AH = u) : e !== this._$AH && e !== S && this._(e) : e._$litType$ !== void 0 ? this.$(e) : e.nodeType !== void 0 ? this.T(e) : Ie(e) ? this.k(e) : this._(e);
  }
  O(e) {
    return this._$AA.parentNode.insertBefore(e, this._$AB);
  }
  T(e) {
    this._$AH !== e && (this._$AR(), this._$AH = this.O(e));
  }
  _(e) {
    this._$AH !== u && M(this._$AH) ? this._$AA.nextSibling.data = e : this.T(w.createTextNode(e)), this._$AH = e;
  }
  $(e) {
    var n;
    const { values: t, _$litType$: i } = e, r = typeof i == "number" ? this._$AC(e) : (i.el === void 0 && (i.el = R.createElement(xe(i.h, i.h[0]), this.options)), i);
    if (((n = this._$AH) == null ? void 0 : n._$AD) === r) this._$AH.p(t);
    else {
      const o = new Ve(r, this), a = o.u(this.options);
      o.p(t), this.T(a), this._$AH = o;
    }
  }
  _$AC(e) {
    let t = _e.get(e.strings);
    return t === void 0 && _e.set(e.strings, t = new R(e)), t;
  }
  k(e) {
    te(this._$AH) || (this._$AH = [], this._$AR());
    const t = this._$AH;
    let i, r = 0;
    for (const n of e) r === t.length ? t.push(i = new z(this.O(N()), this.O(N()), this, this.options)) : i = t[r], i._$AI(n), r++;
    r < t.length && (this._$AR(i && i._$AB.nextSibling, r), t.length = r);
  }
  _$AR(e = this._$AA.nextSibling, t) {
    var i;
    for ((i = this._$AP) == null ? void 0 : i.call(this, !1, !0, t); e !== this._$AB; ) {
      const r = he(e).nextSibling;
      he(e).remove(), e = r;
    }
  }
  setConnected(e) {
    var t;
    this._$AM === void 0 && (this._$Cv = e, (t = this._$AP) == null || t.call(this, e));
  }
}
class K {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(e, t, i, r, n) {
    this.type = 1, this._$AH = u, this._$AN = void 0, this.element = e, this.name = t, this._$AM = r, this.options = n, i.length > 2 || i[0] !== "" || i[1] !== "" ? (this._$AH = Array(i.length - 1).fill(new String()), this.strings = i) : this._$AH = u;
  }
  _$AI(e, t = this, i, r) {
    const n = this.strings;
    let o = !1;
    if (n === void 0) e = C(this, e, t, 0), o = !M(e) || e !== this._$AH && e !== S, o && (this._$AH = e);
    else {
      const a = e;
      let l, c;
      for (e = n[0], l = 0; l < n.length - 1; l++) c = C(this, a[i + l], t, l), c === S && (c = this._$AH[l]), o || (o = !M(c) || c !== this._$AH[l]), c === u ? e = u : e !== u && (e += (c ?? "") + n[l + 1]), this._$AH[l] = c;
    }
    o && !r && this.j(e);
  }
  j(e) {
    e === u ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
  }
}
class We extends K {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(e) {
    this.element[this.name] = e === u ? void 0 : e;
  }
}
class Ke extends K {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(e) {
    this.element.toggleAttribute(this.name, !!e && e !== u);
  }
}
class Ye extends K {
  constructor(e, t, i, r, n) {
    super(e, t, i, r, n), this.type = 5;
  }
  _$AI(e, t = this) {
    if ((e = C(this, e, t, 0) ?? u) === S) return;
    const i = this._$AH, r = e === u && i !== u || e.capture !== i.capture || e.once !== i.once || e.passive !== i.passive, n = e !== u && (i === u || r);
    r && this.element.removeEventListener(this.name, this, i), n && this.element.addEventListener(this.name, this, e), this._$AH = e;
  }
  handleEvent(e) {
    var t;
    typeof this._$AH == "function" ? this._$AH.call(((t = this.options) == null ? void 0 : t.host) ?? this.element, e) : this._$AH.handleEvent(e);
  }
}
class Fe {
  constructor(e, t, i) {
    this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = i;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(e) {
    C(this, e);
  }
}
const Z = U.litHtmlPolyfillSupport;
Z == null || Z(R, z), (U.litHtmlVersions ?? (U.litHtmlVersions = [])).push("3.3.3");
const Xe = (s, e, t) => {
  const i = (t == null ? void 0 : t.renderBefore) ?? e;
  let r = i._$litPart$;
  if (r === void 0) {
    const n = (t == null ? void 0 : t.renderBefore) ?? null;
    i._$litPart$ = r = new z(e.insertBefore(N(), n), n, void 0, t ?? {});
  }
  return r._$AI(s), r;
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const y = globalThis;
class E extends x {
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
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = Xe(t, this.renderRoot, this.renderOptions);
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
var ge;
E._$litElement$ = !0, E.finalized = !0, (ge = y.litElementHydrateSupport) == null || ge.call(y, { LitElement: E });
const G = y.litElementPolyfillSupport;
G == null || G({ LitElement: E });
(y.litElementVersions ?? (y.litElementVersions = [])).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const Ee = (s) => (e, t) => {
  t !== void 0 ? t.addInitializer(() => {
    customElements.define(s, e);
  }) : customElements.define(s, e);
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const Ze = { attribute: !0, type: String, converter: L, reflect: !1, hasChanged: ee }, Ge = (s = Ze, e, t) => {
  const { kind: i, metadata: r } = t;
  let n = globalThis.litPropertyMetadata.get(r);
  if (n === void 0 && globalThis.litPropertyMetadata.set(r, n = /* @__PURE__ */ new Map()), i === "setter" && ((s = Object.create(s)).wrapped = !0), n.set(t.name, s), i === "accessor") {
    const { name: o } = t;
    return { set(a) {
      const l = e.get.call(this);
      e.set.call(this, a), this.requestUpdate(o, l, s, !0, a);
    }, init(a) {
      return a !== void 0 && this.C(o, void 0, s, a), a;
    } };
  }
  if (i === "setter") {
    const { name: o } = t;
    return function(a) {
      const l = this[o];
      e.call(this, a), this.requestUpdate(o, l, s, !0, a);
    };
  }
  throw Error("Unsupported decorator location: " + i);
};
function ie(s) {
  return (e, t) => typeof t == "object" ? Ge(s, e, t) : ((i, r, n) => {
    const o = r.hasOwnProperty(n);
    return r.constructor.createProperty(n, i), o ? Object.getOwnPropertyDescriptor(r, n) : void 0;
  })(s, e, t);
}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
function se(s) {
  return ie({ ...s, state: !0, attribute: !1 });
}
const Je = [
  "fajr",
  "dhuhr",
  "asr",
  "maghrib",
  "ishaa"
], Qe = "shuruq", et = /* @__PURE__ */ new Set([
  "midnight",
  "last_third"
]), tt = /* @__PURE__ */ new Set([
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
function Se(s) {
  return s ? ["fajr", Qe, "dhuhr", "asr", "maghrib", "ishaa"] : [...Je];
}
function it(s, e) {
  return et.has(s) || tt.has(s) ? !1 : Se(e).includes(s);
}
function $e(s, e) {
  const i = Se(e).indexOf(s);
  return i === -1 ? 999 : i;
}
const st = "mawaqeet", rt = "mdi:mosque";
function nt(s) {
  var t;
  return s.translation_key ? s.translation_key : ((t = s.entity_id.split(".").pop()) == null ? void 0 : t.split("_").pop()) ?? null;
}
function ot(s, e, t) {
  if (!e || !s.entities)
    return [];
  const i = [];
  for (const n of Object.values(s.entities)) {
    if (n.platform !== st || n.device_id !== e || !n.entity_id.startsWith("sensor."))
      continue;
    const o = nt(n);
    if (!o || !it(o, t))
      continue;
    const a = s.states[n.entity_id];
    if (!a || a.state === "unavailable" || a.state === "unknown")
      continue;
    const l = a.attributes.device_class;
    if (l && l !== "timestamp")
      continue;
    const c = new Date(a.state);
    Number.isNaN(c.getTime()) || i.push({
      entity_id: n.entity_id,
      prayer_key: o,
      label: lt(s, n, a),
      icon: a.attributes.icon || rt,
      at: c,
      state: a
    });
  }
  i.sort(
    (n, o) => $e(n.prayer_key, t) - $e(o.prayer_key, t)
  );
  const r = t ? 6 : at;
  return i.length < r ? [] : i;
}
const at = 5;
function Y(s, e = /* @__PURE__ */ new Date()) {
  if (s.length === 0)
    return null;
  const t = s.filter((n) => n.at.getTime() > e.getTime());
  if (t.length > 0)
    return {
      prayer: t[0],
      following: t[1] ?? null,
      isTomorrow: !1
    };
  const i = s.find((n) => n.prayer_key === "fajr") ?? s[0], r = s.find((n) => n.prayer_key !== i.prayer_key) ?? null;
  return {
    prayer: i,
    following: r,
    isTomorrow: !0
  };
}
function lt(s, e, t) {
  var i;
  if (e.translation_key) {
    const r = `component.mawaqeet.entity.sensor.${e.translation_key}.name`, n = (i = s.localize) == null ? void 0 : i.call(s, r);
    if (n && n !== r)
      return n;
  }
  return t.attributes.friendly_name || e.entity_id;
}
function P(s, e, t) {
  var r, n;
  const i = t === "12" || t === "system" && ((r = e.locale) == null ? void 0 : r.time_format) === "12";
  return new Intl.DateTimeFormat(((n = e.locale) == null ? void 0 : n.language) || void 0, {
    hour: "numeric",
    minute: "2-digit",
    hour12: i
  }).format(s);
}
function re(s, e = /* @__PURE__ */ new Date(), t = !1) {
  const i = s.getTime() - e.getTime();
  if (t && i < 0) {
    const r = new Date(s);
    return r.setDate(r.getDate() + 1), ve(r.getTime() - e.getTime());
  }
  return ve(i);
}
function ve(s) {
  const e = Math.abs(s), t = Math.round(e / 6e4);
  if (t < 1)
    return s >= 0 ? "now" : "just now";
  if (t < 60)
    return s >= 0 ? `in ${t}m` : `${t}m ago`;
  const i = Math.floor(t / 60), r = t % 60;
  if (i < 24) {
    const o = r > 0 ? `${i}h ${r}m` : `${i}h`;
    return s >= 0 ? `in ${o}` : `${o} ago`;
  }
  const n = Math.floor(i / 24);
  return s >= 0 ? `in ${n}d` : `${n}d ago`;
}
function ct(s, e) {
  var i;
  const t = (i = s.devices) == null ? void 0 : i[e];
  return t ? t.name_by_user || t.name || e : "";
}
function ht(s) {
  switch (s) {
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
        min_rows: 2,
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
function D(s, e) {
  return e.time_format ?? "system";
}
function H(s, e) {
  if (!e.show_device_name || !e.device)
    return u;
  const t = ct(s, e.device);
  return t ? p`<div class="header">${t}</div>` : u;
}
function V(s) {
  return p`<div class="error">${s}</div>`;
}
function q(s) {
  return p`<ha-icon .icon=${s}></ha-icon>`;
}
function j(s, e) {
  return (t) => {
    t.stopPropagation(), e(s);
  };
}
function Ce(s, e, t, i, r) {
  const n = Y(t, i);
  if (!n)
    return V("No prayer times available.");
  const { prayer: o, following: a, isTomorrow: l } = n, c = D(s, e), d = re(o.at, i, l), h = P(o.at, s, c), m = a && p`Following: ${a.label} at ${P(a.at, s, c)}`;
  return p`
    ${H(s, e)}
    <div
      class="next-hero"
      @click=${j(o.entity_id, r)}
      role="button"
      tabindex="0"
    >
      ${q(o.icon)}
      <div class="prayer-name">${o.label}</div>
      <div class="countdown">${d} · ${h}</div>
      ${l ? p`<div class="following">Tomorrow</div>` : u}
      ${m ? p`<div class="following">${m}</div>` : u}
    </div>
  `;
}
function dt(s, e, t, i, r) {
  const n = Y(t, i), o = n == null ? void 0 : n.prayer.entity_id, a = D(s, e), l = e.show_relative !== !1;
  return p`
    ${H(s, e)}
    ${t.map((c) => {
    const d = c.entity_id === o, h = e.show_passed_style !== !1 && c.at.getTime() < i.getTime(), m = ["row", d ? "next" : "", h ? "passed strike" : ""].filter(Boolean).join(" ");
    return p`
        <div
          class=${m}
          @click=${j(c.entity_id, r)}
          role="button"
          tabindex="0"
        >
          ${q(c.icon)}
          <span class="name">${c.label}</span>
          <span class="times">
            <div>${P(c.at, s, a)}</div>
            ${l ? p`<div class="relative">
                  ${re(c.at, i)}
                </div>` : u}
          </span>
        </div>
      `;
  })}
  `;
}
function Pe(s, e, t, i, r) {
  const n = Y(t, i), o = n == null ? void 0 : n.prayer.entity_id, a = D(s, e), l = e.show_relative === !0;
  return p`
    ${H(s, e)}
    <div class="horizontal">
      ${t.map((c) => {
    const d = c.entity_id === o, h = e.show_passed_style !== !1 && c.at.getTime() < i.getTime(), m = ["chip", d ? "next" : "", h ? "passed" : ""].filter(Boolean).join(" ");
    return p`
          <div
            class=${m}
            @click=${j(c.entity_id, r)}
            role="button"
            tabindex="0"
          >
            ${q(c.icon)}
            <div>${c.label}</div>
            <div class="chip-time">${P(c.at, s, a)}</div>
            ${l ? p`<div class="chip-relative">
                  ${re(c.at, i)}
                </div>` : u}
          </div>
        `;
  })}
    </div>
  `;
}
function ut(s, e, t, i, r) {
  return p`
    ${Ce(s, { ...e, show_device_name: !1 }, t, i, r)}
    <hr class="divider" />
    ${Pe(
    s,
    { ...e, show_device_name: !1, show_relative: !1 },
    t,
    i,
    r
  )}
  `;
}
function pt(s, e, t, i, r) {
  const n = Y(t, i), o = n == null ? void 0 : n.prayer.entity_id, a = t.filter((h) => h.at.getTime() > i.getTime()), l = t.filter((h) => h.at.getTime() <= i.getTime()), c = D(s, e), d = (h, m) => p`
    <div class="section-title">${h}</div>
    ${m.map((f) => {
    const A = f.entity_id === o, ne = l.includes(f), Te = ["row", A ? "next" : "", ne ? "passed" : ""].filter(Boolean).join(" ");
    return p`
        <div
          class=${Te}
          @click=${j(f.entity_id, r)}
          role="button"
          tabindex="0"
        >
          ${ne ? p`<span class="agenda-check">✓</span>` : u}
          ${q(f.icon)}
          <span class="name">${f.label}</span>
          <span class="times">${P(f.at, s, c)}</span>
        </div>
      `;
  })}
  `;
  return p`
    ${H(s, e)}
    ${l.length ? d("Earlier today", l) : u}
    ${a.length ? d("Upcoming", a) : d("Upcoming", t)}
  `;
}
function mt(s, e, t, i, r) {
  if (t.length < 2)
    return V("Not enough prayer times for timeline.");
  const n = t[0].at.getTime(), a = t[t.length - 1].at.getTime() - n || 1, l = Math.min(100, Math.max(0, (i.getTime() - n) / a * 100)), c = D(s, e);
  return p`
    ${H(s, e)}
    <div class="timeline">
      <div class="timeline-track"></div>
      <div class="timeline-now" style="left: ${l}%"></div>
      ${t.map((d) => {
    const h = (d.at.getTime() - n) / a * 100;
    return p`
          <div
            class="timeline-marker"
            style="left: ${h}%"
            @click=${j(d.entity_id, r)}
            role="button"
            tabindex="0"
          >
            ${q(d.icon)}
            <div>${d.label}</div>
            <div>${P(d.at, s, c)}</div>
          </div>
        `;
  })}
    </div>
  `;
}
function ft(s, e, t, i, r) {
  switch (e.layout ?? "next") {
    case "horizontal":
      return Pe(s, e, t, i, r);
    case "vertical":
      return dt(s, e, t, i, r);
    case "combined":
      return ut(s, e, t, i, r);
    case "timeline":
      return mt(s, e, t, i, r);
    case "agenda":
      return pt(s, e, t, i, r);
  }
  return Ce(s, e, t, i, r);
}
const _t = ke`
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
    margin-bottom: 12px;
  }

  .error {
    color: var(--error-color, #b71c1c);
    padding: 8px 0;
  }

  .row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 4px;
    border-radius: 8px;
    cursor: pointer;
  }

  .row:hover {
    background: var(--secondary-background-color, rgba(0, 0, 0, 0.05));
  }

  .row.next {
    font-weight: 600;
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
  }

  .row.passed {
    opacity: 0.45;
  }

  .row.passed.strike {
    text-decoration: line-through;
  }

  .row ha-icon {
    --mdc-icon-size: 22px;
    color: var(--primary-color);
    flex-shrink: 0;
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
  }

  .next-hero ha-icon {
    --mdc-icon-size: 48px;
    color: var(--primary-color);
  }

  .next-hero .prayer-name {
    font-size: 1.5em;
    font-weight: 600;
    margin: 8px 0 4px;
  }

  .next-hero .countdown {
    font-size: 1.25em;
    color: var(--primary-color);
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
    padding: 8px 10px;
    border-radius: 8px;
    min-width: 4.5em;
    border: 1px solid transparent;
    cursor: pointer;
  }

  .chip.next {
    border-color: var(--primary-color);
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
    font-weight: 600;
  }

  .chip.passed {
    opacity: 0.45;
  }

  .chip ha-icon {
    --mdc-icon-size: 20px;
    color: var(--primary-color);
  }

  .chip .chip-time {
    font-size: 0.95em;
    margin-top: 4px;
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
    opacity: 0.6;
    margin: 8px 0 4px;
  }

  .timeline {
    position: relative;
    height: 48px;
    margin: 24px 8px 32px;
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
    font-size: 0.65em;
    white-space: nowrap;
  }

  .timeline-marker ha-icon {
    --mdc-icon-size: 16px;
    color: var(--primary-color);
  }

  .timeline-now {
    position: absolute;
    top: -4px;
    width: 2px;
    height: 56px;
    background: var(--accent-color, var(--primary-color));
    transform: translateX(-50%);
    z-index: 1;
  }

  .agenda-check {
    opacity: 0.5;
    margin-inline-end: 4px;
  }
`;
var $t = Object.defineProperty, vt = Object.getOwnPropertyDescriptor, b = (s, e, t, i) => {
  for (var r = i > 1 ? void 0 : i ? vt(e, t) : e, n = s.length - 1, o; n >= 0; n--)
    (o = s[n]) && (r = (i ? o(e, t, r) : o(r)) || r);
  return i && r && $t(e, t, r), r;
};
let T = class extends E {
  constructor() {
    super(...arguments), this._now = /* @__PURE__ */ new Date();
  }
  setConfig(s) {
    if (!s.device)
      throw new Error("Set a Mawaqeet device for this card.");
    this._config = {
      type: "custom:mawaqeet-prayer-card",
      layout: "next",
      show_shuruq: !1,
      show_passed_style: !0,
      time_format: "system",
      show_relative: !0,
      show_device_name: !1,
      ...s
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
    const s = ((e = this._config) == null ? void 0 : e.layout) ?? "next";
    return ht(s);
  }
  static async getConfigElement() {
    return document.createElement("mawaqeet-prayer-card-editor");
  }
  static getStubConfig() {
    return {
      type: "custom:mawaqeet-prayer-card",
      layout: "next",
      show_shuruq: !1
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
  willUpdate(s) {
    s.has("hass") && (this._now = /* @__PURE__ */ new Date());
  }
  render() {
    if (!this.hass || !this._config)
      return p`<ha-card><div class="error">Loading…</div></ha-card>`;
    const s = this._config.show_shuruq === !0, e = ot(
      this.hass,
      this._config.device,
      s
    );
    let t;
    return this._config.device ? e.length === 0 ? t = V(
      "No prayer times found for this device. Check that Mawaqeet is loaded."
    ) : t = ft(
      this.hass,
      this._config,
      e,
      this._now,
      (i) => this._moreInfo(i)
    ) : t = V("Select a Mawaqeet location device in card settings."), p`<ha-card>${t}</ha-card>`;
  }
  _moreInfo(s) {
    const e = new CustomEvent("hass-more-info", {
      bubbles: !0,
      composed: !0,
      detail: { entityId: s }
    });
    this.dispatchEvent(e);
  }
};
T.styles = _t;
b([
  ie({ attribute: !1 })
], T.prototype, "hass", 2);
b([
  se()
], T.prototype, "_config", 2);
b([
  se()
], T.prototype, "_now", 2);
T = b([
  Ee("mawaqeet-prayer-card")
], T);
const gt = [
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
  { name: "show_device_name", selector: { boolean: {} } }
];
let W = class extends E {
  setConfig(s) {
    this._config = s;
  }
  render() {
    return !this.hass || !this._config ? p`` : p`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${gt}
        .computeLabel=${(s) => yt[s.name] ?? s.name}
        @value-changed=${this._changed}
      ></ha-form>
    `;
  }
  _changed(s) {
    s.stopPropagation();
    const e = s.detail.value;
    this._config = e;
    const t = new CustomEvent("config-changed", {
      detail: { config: e },
      bubbles: !0,
      composed: !0
    });
    this.dispatchEvent(t);
  }
};
b([
  ie({ attribute: !1 })
], W.prototype, "hass", 2);
b([
  se()
], W.prototype, "_config", 2);
W = b([
  Ee("mawaqeet-prayer-card-editor")
], W);
const yt = {
  device: "Mawaqeet location",
  layout: "Layout",
  show_shuruq: "Show Shuruq (sunrise)",
  show_passed_style: "Dim passed prayers",
  time_format: "Time format",
  show_relative: "Show relative times",
  show_device_name: "Show location name"
};
typeof window < "u" && (window.customCards = window.customCards || [], window.customCards.push({
  type: "mawaqeet-prayer-card",
  name: "Mawaqeet Prayer",
  description: "Prayer times from a Mawaqeet location device",
  preview: !0
}));
export {
  T as MawaqeetPrayerCard,
  W as MawaqeetPrayerCardEditor
};
