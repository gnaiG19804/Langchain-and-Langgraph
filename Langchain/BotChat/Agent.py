import os
import json
import uuid
import asyncio
import requests
import psycopg2
from dotenv import load_dotenv
import uuid
import psycopg2

# Import LangChain & Groq
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.mongodb import MongoDBSaver

# Import Database
from pymongo import MongoClient
from neon import init_neon_db

# Import Telegram
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- 1. CẤU HÌNH HỆ THỐNG ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
POSTGRES_URL = os.getenv("POSTGRES_URL")
MONGO_URL = os.getenv("MONGO_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_PRODUCT = "https://script.googleusercontent.com/macros/echo?user_content_key=AehSKLj1E5k_VlAhY8UCy3HB5YE-fYFIRDy22Fnq68xvtdr2C2zZzUacGfx2hqCocLOnp-CzAqC1ecn_JTzdqj3iwko0HJI3pMAWPHpmkdNmggw-OUxkOqSY9DWQaIIyIun3UsS757L08C_kbUEWNiM6dWwW4U-qWmPO5My_4MvViISSNJ_jxSBOmK8B3G9hKrgGRAI-0pLsYHbCwsb5Z75zfyYgJR68vDnSP7koKvJzB1N7EpP7uWh06tLfiLtObQVteOh7PAQNe8XOfsCrcFTxDtu-MXqhLRrj94rz_zL9&lib=Ms093gOttmwBjxOrb4f6MKsaVKqHWbGzI"

# Kiểm tra biến môi trường
if not all([TELEGRAM_TOKEN, MONGO_URL, GROQ_API_KEY]):
    print("❌ LỖI: Thiếu biến môi trường trong file .env")
    exit()

# --- 2. KẾT NỐI MONGODB ---
try:
    client = MongoClient(MONGO_URL)
    # Ping thử để check kết nối
    client.admin.command('ping')
    print(">>> ✅ Kết nối MongoDB thành công!")
except Exception as e:
    print(f">>> ❌ Lỗi kết nối MongoDB: {e}")
    exit()

memory = MongoDBSaver(client)

# --- 3. ĐỊNH NGHĨA CÔNG CỤ (TOOLS) ---

def safe_int(value):
    """Hàm phụ trợ: Ép kiểu sang số nguyên an toàn, tránh lỗi khi API trả về chuỗi rỗng"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def format_currency(value):
    """Hàm phụ trợ: Định dạng tiền tệ"""
    try:
        return f"{int(value):,}".replace(",", ".")
    except:
        return str(value)
init_neon_db(POSTGRES_URL)

@tool
def create_order(ho_ten: str, sdt: str, dia_chi: str, danh_sach_mon: str) -> str:
    """
    Dùng để chốt đơn hàng và lưu vào hệ thống Neon Database.
    CHỈ DÙNG khi khách đã cung cấp ĐỦ 3 thông tin: Tên, SĐT, Địa chỉ.
    """
    conn = None
    try:
        # 1. Tạo mã đơn hàng ngẫu nhiên (VD: #A1B2C)
        order_code = f"#{str(uuid.uuid4())[:5].upper()}"
        
        # 2. Kết nối Neon
        conn = psycopg2.connect(POSTGRES_URL)
        cur = conn.cursor()
        
        # 3. Chèn dữ liệu (SQL Insert)
        sql = """
            INSERT INTO orders (order_code, customer_name, phone, address, items, status)
            VALUES (%s, %s, %s, %s, %s, 'MOI_TAO')
        """
        cur.execute(sql, (order_code, ho_ten, sdt, dia_chi, danh_sach_mon))
        conn.commit()
        
        cur.close()
        
        # 4. Trả về thông báo thành công
        return f"🎉 Đã chốt đơn thành công! Mã đơn: *{order_code}*.\nĐơn hàng đã được lưu an toàn trên Neon Cloud."

    except Exception as e:
        return f"❌ Lỗi hệ thống khi lưu đơn: {e}"
    finally:
        if conn: conn.close()

@tool
def get_all_products() -> str:
    """
    Lấy danh sách TẤT CẢ sản phẩm MixiFood trong kho.
    Dùng khi khách hỏi: bán gì, có những món nào, xem menu.
    """
    try:
        response = requests.get(API_PRODUCT, timeout=10)
        if response.status_code != 200:
            return "❌ Không thể kết nối kho sản phẩm."

        products = response.json()
        if not products:
            return "📦 Hiện tại kho chưa có sản phẩm nào."

        output = "🛒 *MENU MIXIFOOD* 🛒\n"
        output += "━" * 15 + "\n\n"
        
        for i, sp in enumerate(products, 1):
            name = sp.get("name", "Sản phẩm")
            price = sp.get("price", 0)
            stock = safe_int(sp.get("stock", 0))
            
            price_fmt = format_currency(price)
            
            # Icon tình trạng kho
            if stock > 0:
                stock_text = f"✅ Còn {stock}"
            else:
                stock_text = "❌ Hết hàng"
            
            output += f"{i}. *{name}*\n"
            output += f"   💰 {price_fmt} VND\n"
            output += f"   {stock_text}\n\n"
        
        output += "━" * 15 + "\n"
        output += " Nhắn tên món để mình tư vấn kỹ hơn nha!"
        return output

    except Exception as e:
        return f" Lỗi hệ thống: {e}"

@tool 
def search_product(product_name: str) -> str:
    """
    Tìm kiếm sản phẩm theo tên hoặc từ khóa.
    Dùng khi khách hỏi cụ thể về một món nào đó (giá bao nhiêu, còn không).
    """
    try:
        response = requests.get(API_PRODUCT, timeout=10)
        if response.status_code != 200:
            return " Không kết nối được kho sản phẩm."

        products = response.json()
        
        # Tách query thành các từ khóa
        keywords = [w.lower() for w in product_name.split() if len(w) >= 2]
        if not keywords:
            return " Bạn nhập tên món cụ thể hơn chút nha."

        matched_products = []
        for sp in products:
            name = str(sp.get("name", "")).lower()
            match_count = sum(1 for kw in keywords if kw in name)
            
            if match_count > 0:
                matched_products.append({"data": sp, "score": match_count})
        
        # Sắp xếp theo độ khớp
        matched_products.sort(key=lambda x: x["score"], reverse=True)
        
        if not matched_products:
            return f"❌ Không tìm thấy món nào tên là '{product_name}' trong kho ạ."

        results = []
        for item in matched_products[:5]: # Lấy top 5
            sp = item["data"]
            price = format_currency(sp.get("price", 0))
            stock = safe_int(sp.get("stock", 0))
            
            stock_text = f"✅ Còn {stock}" if stock > 0 else "❌ Hết hàng"
            
            results.append(
                f"🍽 *{sp['name']}*\n"
                f"   💰 Giá: {price} VND\n"
                f"   {stock_text}"
            )

        output = f"🔍 *Kết quả tìm: '{product_name}'*\n\n"
        output += "\n\n".join(results)
        return output

    except Exception as e:
        return f"⚠️ Lỗi tra cứu: {e}"

# --- 4. KHỞI TẠO AGENT ---

# Model chính xác cho Groq
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

SYSTEM_PROMPT = """
Bạn là AI Agent bán hàng tên là "Bộ ii" của quán MixiFood.
Phong cách: Vui vẻ, thân thiện, hơi tếu táo một chút (nhưng vẫn lễ phép), xưng "mình" gọi "bạn" hoặc "anh/chị".

QUY TẮC QUAN TRỌNG:
1. Khi khách hỏi về món ăn/giá cả/tồn kho -> BẮT BUỘC dùng tool (`search_product` hoặc `get_all_products`).
2. Tuyệt đối KHÔNG được tự bịa ra giá tiền.
3. Nếu tool trả về kết quả, hãy gửi nguyên văn thông tin đó, chỉ thêm thắt lời dẫn vui vẻ.
4. Nếu khách hỏi chuyện ngoài lề (thời tiết, bóng đá...), cứ trả lời giao lưu bình thường.
5. Khi khách muốn ĐẶT HÀNG và đã cung cấp ĐỦ: Tên, SĐT, Địa chỉ, Món -> Dùng tool `create_order` để lưu đơn.
6. Nếu khách muốn đặt nhưng THIẾU thông tin, hãy hỏi lại từng phần còn thiếu.

Đừng tự ý vẽ bảng markdown phức tạp, cứ liệt kê rõ ràng là được.
"""

agent = create_react_agent(
    model=llm,
    tools=[get_all_products, search_product, create_order],
    checkpointer=memory,
)

# --- 5. XỬ LÝ TELEGRAM (ASYNC) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Hé lô {user_name}! 👋\n"
        f"Mình là Bộ ii đây. Bạn đang đói bụng hơm? Muốn xem menu hay tìm món gì cứ bảo mình nhé!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    
    # Định danh Thread ID cho MongoDB
    thread_id = f"telegram_{user_id}"
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"📩 Tin nhắn từ {user_id} ({update.effective_user.first_name}): {user_text}")

    # Hiển thị trạng thái "Typing..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    inputs = {
        "messages": [
            ("system", SYSTEM_PROMPT),
            ("user", user_text)
        ]
    }

    try:
        # Dùng ainvoke (Async Invoke) để không bị đơ bot khi có nhiều người chat
        response = await agent.ainvoke(inputs, config=config)
        
        # Lấy câu trả lời cuối cùng
        if response["messages"]:
            bot_reply = response["messages"][-1].content
            
            # Gửi tin nhắn (Thử Markdown trước, nếu lỗi thì gửi plain text)
            try:
                await update.message.reply_text(bot_reply, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                # Fallback nếu Markdown bị lỗi ký tự đặc biệt
                await update.message.reply_text(bot_reply)
        else:
            await update.message.reply_text("🤔 Ồ, mình đang bị lag xíu, bạn hỏi lại được không?")

    except Exception as e:
        print(f"❌ Lỗi Agent: {e}")
        await update.message.reply_text("Ui da, não bộ mình đang bảo trì xíu. Thử lại sau nha!")

# --- 6. CHẠY BOT ---
if __name__ == '__main__':
    print(" Bot MixiFood đang khởi động...")
    
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print(" Bot đang chạy! (Nhấn Ctrl+C để dừng)")
    application.run_polling()