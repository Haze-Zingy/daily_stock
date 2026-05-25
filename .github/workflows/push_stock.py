import os
import requests
import akshare as ak
from datetime import datetime

def get_stock_realtime(code):
    """获取单只股票的实时行情（包含K线关键数据）"""
    try:
        # akshare 获取A股实时行情
        df = ak.stock_zh_a_spot_em()
        # 标准化代码格式（去掉可能的前后缀）
        code_clean = code.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        row = df[df['代码'] == code_clean]
        if row.empty:
            return None
        name = row['名称'].values[0]
        open_price = row['今开'].values[0]
        close_price = row['最新价'].values[0]
        high = row['最高'].values[0]
        low = row['最低'].values[0]
        volume = row['成交量'].values[0]
        change_pct = row['涨跌幅'].values[0]
        return {
            'name': name,
            'code': code_clean,
            'open': open_price,
            'close': close_price,
            'high': high,
            'low': low,
            'volume': volume,
            'change_pct': change_pct
        }
    except Exception as e:
        print(f"Error fetching {code}: {e}")
        return None

def send_to_feishu(webhook, content):
    try:
        resp = requests.post(webhook, json={"msg_type": "text", "content": {"text": content}})
        print(f"Feishu response: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Send error: {e}")

if __name__ == "__main__":
    webhook = os.environ.get("FEISHU_WEBHOOK")
    stock_list_str = os.environ.get("STOCK_LIST", "")
    stock_codes = [c.strip() for c in stock_list_str.split(",") if c.strip()]

    if not webhook:
        print("❌ FEISHU_WEBHOOK not set")
        exit(1)
    if not stock_codes:
        print("❌ STOCK_LIST not set")
        exit(1)

    msg = f"📊 股票数据日报 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    for code in stock_codes:
        data = get_stock_realtime(code)
        if data:
            msg += f"• {data['name']} ({data['code']})\n"
            msg += f"  开 {data['open']} 收 {data['close']} 高 {data['high']} 低 {data['low']}\n"
            msg += f"  涨跌幅 {data['change_pct']:.2f}% 成交量 {data['volume']}\n\n"
        else:
            msg += f"• {code} 未获取到数据\n\n"

    send_to_feishu(webhook, msg)
