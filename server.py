#!/usr/bin/env python3
"""
简单 Flask 服务：使用 AkShare 获取 A 股融资融券当日数据，并返回 JSON。
安装依赖: pip install -r requirements.txt
运行: python3 server.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)

# 延迟导入 akshare，因为在没有安装时保留清晰报错
def try_get_akshare_data(date, stock=None):
    try:
        import akshare as ak
        import pandas as pd
        # 优先使用明确的 akshare 接口
        records = []
        # 转为 akshare 常用的 YYYYMMDD 格式
        date_arg = date.replace('-', '')
        # 如果请求指定了某只股票，先获取当日明细（上交所或深交所），再按 code 过滤
        if stock:
            df = None
            if hasattr(ak, 'stock_margin_detail_sse'):
                try:
                    df = ak.stock_margin_detail_sse(date_arg)
                except Exception:
                    df = None
            if (df is None) and hasattr(ak, 'stock_margin_detail_szse'):
                try:
                    df = ak.stock_margin_detail_szse(date_arg)
                except Exception:
                    df = None
            if df is not None:
                records = pd.DataFrame(df).to_dict(orient='records')
                # 过滤代码，可能字段名不同，使用包含匹配
                def matches_stock(rec):
                    # 检查任意字段值是否包含指定代码（宽松匹配）
                    for v in rec.values():
                        if v and str(stock) in str(v):
                            return True
                    return False
                records = [r for r in records if matches_stock(r)]
        else:
            # 优先尝试上交所的日度汇总接口
            if hasattr(ak, 'stock_margin_sse'):
                try:
                    df = ak.stock_margin_sse(start_date=date_arg, end_date=date_arg)
                    records = pd.DataFrame(df).to_dict(orient='records')
                except Exception:
                    records = []
            # 再尝试深市相关接口
            if not records and hasattr(ak, 'stock_margin_szse'):
                try:
                    df = ak.stock_margin_szse(date_arg)
                    records = pd.DataFrame(df).to_dict(orient='records')
                except Exception:
                    records = []

        # 若未通过专用接口获取到数据，则直接返回空列表（前端会回退到演示数据）
        if not records:
            return []

        # 如果拿到了 records，则继续下面的字段标准化流程
        # 将 DataFrame 记录标准化为前端需要的字段
        # 标准化字段，放到 mapped 列表中
        mapped = []
        for rec in records:
            # 确保是 dict
            if not isinstance(rec, dict):
                try:
                    rec = dict(rec)
                except Exception:
                    rec = {}
            r = {}
            # 自动化字段匹配：优先查找含关键词的字段名
            keys = list(rec.keys())
            lower_keys = {k: k.lower() for k in keys}

            def pick(key_subs):
                for k in keys:
                    lk = k.lower()
                    for sub in key_subs:
                        if sub in lk:
                            return rec.get(k)
                return None

            # code/name
            code = pick(['代码', 'ts_code', 'code', 'stock_code', 'symbol', '标的证券代码', '证券代码'])
            name = pick(['名称', 'name', '证券简称', 'stock_name', '标的证券简称'])
            r['code'] = code or ''
            r['name'] = name or ''

            # 数值字段
            r['financing_balance'] = pick(['融资余额', 'financing_balance', 'rzye', 'margin_balance', 'rz_blance', 'margin'])
            r['securities_lending_balance'] = pick(['融券余额', 'securities_lending_balance', 'rqye', 'short_balance', 'short', '融券余额'])
            r['financing_buy_amount'] = pick(['融资买入额', 'financing_buy_amount', 'rzmre', 'financing_buy'])
            r['securities_lending_sell_volume'] = pick(['融券卖出量', 'securities_lending_sell_volume', 'rqsell', 'short_sell', 'sell_volume', '融券卖出量'])

            # 尝试把 pandas 标量转成原生类型
            def normalize(v):
                try:
                    # pandas types have values attribute
                    import pandas as _pd
                    if hasattr(v, 'item'):
                        return v.item()
                except Exception:
                    pass
                return v

            for k in ('financing_balance','securities_lending_balance','financing_buy_amount','securities_lending_sell_volume'):
                if r.get(k) is not None:
                    r[k] = normalize(r[k])

            # 保留原始记录
            r['_raw'] = rec
            mapped.append(r)
        return mapped
        raise RuntimeError('未能通过 akshare 的候选函数获取数据，请参考 akshare 文档或升级 akshare 版本')
    except Exception as e:
        raise

@app.route('/api/margin')
def api_margin():
    date = request.args.get('date')
    pageSize = int(request.args.get('pageSize', 100))
    stock = request.args.get('stock')
    try:
        if not date:
            return jsonify({'error': 'missing date parameter'}), 400
        try:
            data = try_get_akshare_data(date, stock=stock)
        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({'error': 'akshare fetch failed', 'detail': str(e), 'traceback': tb}), 500
        # 截断数量
        if isinstance(data, list):
            return jsonify(data[:pageSize])
        else:
            return jsonify({'error': 'unexpected data format from akshare'}), 500
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

if __name__ == '__main__':
    print('Starting server on http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000)
