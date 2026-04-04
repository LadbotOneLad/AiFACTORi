# kotahitanga_sympy.py
# こたひたんが — Kotahitanga Coherence Engine (SymPy)
# ７次元：層・しん・こう・つな・うご・かん・みち

from sympy import symbols, simplify
import json
import sys

# ─────────────────────────────────────────────
# 記号定義 — Ngā Tohu
# 層（Layer）, しん（Identity）, こう（Structure）,
# つな（Topology）, うご（Rhythm）, かん（Security）, みち（Navigation）

層, しん, こう, つな, うご, かん, みち = symbols("層 しん こう つな うご かん みち")
w層, wしん, wこう, wつな, wうご, wかん, wみち = symbols("w層 wしん wこう wつな wうご wかん wみち")

# ─────────────────────────────────────────────
# こたひたんが・式 — Te Ture o te Kotahitanga
#
# K = (Σ w_i * D_i) / (Σ w_i)
# D_i ∈ [0,1]  （各次元の整合度：0=崩壊, 1=完全）

K_expr = (w層*層 + wしん*しん + wこう*こう + wつな*つな +
          wうご*うご + wかん*かん + wみち*みち) / (
          w層 + wしん + wこう + wつな + wうご + wかん + wみち)

K_simplified = simplify(K_expr)

# ─────────────────────────────────────────────
# 既定ウェイト — Ngā Taumaha Tautuhi
# 全て同じ重み（1）＝フラットなこたひたんが

default_weights = {
    w層: 1,
    wしん: 1,
    wこう: 1,
    wつな: 1,
    wうご: 1,
    wかん: 1,
    wみち: 1,
}


def kotahitanga_score(
    層値: float,
    しん値: float,
    こう値: float,
    つな値: float,
    うご値: float,
    かん値: float,
    みち値: float,
    weights: dict = None,
) -> float:
    """
    こたひたんが・スコアを計算する
    Te Tatau i te Kotahitanga (Unity Score)

    各次元値 ∈ [0,1]
      1. 層   — LAYER       (Namespace, StatefulSet, HPA, PVC, Ingress)
      2. しん — IDENTITY    (JWT, RBAC, ServiceAccounts)
      3. こう — STRUCTURE   (Replicas, Probes, Resources)
      4. つな — TOPOLOGY    (ConfigMap, Service, Endpoints)
      5. うご — RHYTHM      (HPA, rollout timing)
      6. かん — SECURITY    (NetworkPolicy, TLS, uid)
      7. みち — NAVIGATION  (gtop-k8, CLI surface)

    weights: 各次元の重み（省略時は全て1）
    """
    if weights is None:
        weights = default_weights

    subs_map = {
        層: 層値,
        しん: しん値,
        こう: こう値,
        つな: つな値,
        うご: うご値,
        かん: かん値,
        みち: みち値,
    }
    subs_map.update(weights)

    val = float(K_simplified.subs(subs_map))
    return val


def kotahitanga_binary(
    pass_flags: dict,
    weights: dict = None,
) -> float:
    """
    バイナリ（PASS/FAIL）からこたひたんがを計算する。
    pass_flags 例:
        {
          "層": True,
          "しん": True,
          "こう": True,
          "つな": False,
          "うご": True,
          "かん": True,
          "みち": True,
        }
    """
    層値   = 1.0 if pass_flags.get("層",   False) else 0.0
    しん値 = 1.0 if pass_flags.get("しん", False) else 0.0
    こう値 = 1.0 if pass_flags.get("こう", False) else 0.0
    つな値 = 1.0 if pass_flags.get("つな", False) else 0.0
    うご値 = 1.0 if pass_flags.get("うご", False) else 0.0
    かん値 = 1.0 if pass_flags.get("かん", False) else 0.0
    みち値 = 1.0 if pass_flags.get("みち", False) else 0.0

    return kotahitanga_score(
        層値, しん値, こう値, つな値, うご値, かん値, みち値, weights
    )


def main():
    """
    stdin から JSON を受け取って、こたひたんがを計算 → JSON で stdout に出力
    """
    try:
        data = json.loads(sys.stdin.read())
        pass_flags = data.get("pass_flags", {})
        weights = data.get("weights", None)
        
        K = kotahitanga_binary(pass_flags, weights)
        
        # 数値をパース（6/7 = 0.857...）
        pass_count = sum(1 for v in pass_flags.values() if v)
        total_count = len(pass_flags)
        
        result = {
            "K": round(K, 4),
            "K_percent": round(K * 100, 2),
            "pass_count": pass_count,
            "total_count": total_count,
            "dimensions": pass_flags,
            "status": "PASS" if K >= 0.857 else "WARN" if K >= 0.5 else "FAIL"
        }
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        error_result = {
            "error": str(e),
            "K": None,
            "status": "ERROR"
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
