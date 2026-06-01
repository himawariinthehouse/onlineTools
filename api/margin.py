from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import traceback

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 处理 CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        try:
            # 解析查询参数
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            date = query_params.get('date', [''])[0]
            page_size = int(query_params.get('pageSize', [100])[0])
            stock = query_params.get('stock', [None])[0]

            if not date:
                self.wfile.write(json.dumps({'error': '缺少 date 参数'}).encode())
                return

            # 获取 Akshare 数据
            data = get_akshare_data(date, stock)
            
            # 限制返回条数
            if len(data) > page_size:
                data = data[:page_size]

            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            error_msg = f"错误: {str(e)}\n{traceback.format_exc()}"
            self.wfile.write(json.dumps({'error': error_msg}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def get_akshare_data(date, stock=None):
    """从 AkShare 获取融资融券数据"""
    try:
        import akshare as ak
        import pandas as pd
        
        records = []
        date_arg = date.replace('-', '')
        
        # 获取数据
        if stock:
            # 如果指定了股票代码
            df = None
            try:
                if hasattr(ak, 'stock_margin_detail_sse'):
                    df = ak.stock_margin_detail_sse(date_arg)
            except:
                pass
            
            if df is None:
                try:
                    if hasattr(ak, 'stock_margin_detail_szse'):
                        df = ak.stock_margin_detail_szse(date_arg)
                except:
                    pass
            
            if df is not None:
                records = pd.DataFrame(df).to_dict(orient='records')
                records = [r for r in records if stock in str(r.values())]
        else:
            # 获取所有数据
            try:
                if hasattr(ak, 'stock_margin_sse'):
                    df = ak.stock_margin_sse(start_date=date_arg, end_date=date_arg)
                    records = pd.DataFrame(df).to_dict(orient='records')
            except:
                pass
            
            if not records:
                try:
                    if hasattr(ak, 'stock_margin_szse'):
                        df = ak.stock_margin_szse(date_arg)
                        records = pd.DataFrame(df).to_dict(orient='records')
                except:
                    pass
        
        # 标准化字段
        mapped = []
        for rec in records:
            if not isinstance(rec, dict):
                try:
                    rec = dict(rec)
                except:
                    rec = {}
            
            r = {}
            keys = list(rec.keys())
            
            def pick(key_subs):
                for k in keys:
                    lk = k.lower()
                    for sub in key_subs:
                        if sub in lk:
                            return rec.get(k)
                return None
            
            r['code'] = pick(['代码', 'ts_code', 'code', 'stock_code', 'symbol']) or ''
            r['name'] = pick(['名称', 'name', '证券简称', 'stock_name']) or ''
            r['financing_balance'] = pick(['融资余额', 'financing_balance', 'rzye']) or 0
            r['securities_lending_balance'] = pick(['融券余额', 'securities_lending_balance', 'rqye']) or 0
            r['financing_buy_amount'] = pick(['融资买入额', 'financing_buy_amount', 'rzmre']) or 0
            r['securities_lending_sell_volume'] = pick(['融券卖出量', 'securities_lending_sell_volume', 'rqsell']) or 0
            
            mapped.append(r)
        
        return mapped if mapped else []
        
    except ImportError:
        return [{'error': 'AkShare 库未安装，请在 Vercel 环境变量中配置'}]
    except Exception as e:
        return [{'error': f'获取数据失败: {str(e)}'}]
