# Filename: nem_mock_demo_vn.py
import streamlit as st
import json
from datetime import datetime, timezone
import time

# --- Dữ liệu Giả (Mock Data) ---
# Định nghĩa các phản hồi mẫu, trông giống thật, cho các input cụ thể

# Địa chỉ ví NEM mẫu (dùng địa chỉ này khi nhập vào ô input)
MOCK_EXAMPLE_ADDRESS = "NACTUS-KR5KHJ-SWT4EK-NE55M7-U74FKW-KEREEE-YSU5"
MOCK_CLEANED_ADDRESS = MOCK_EXAMPLE_ADDRESS.replace("-", "")

# Mã hash giao dịch mẫu (dùng mã hash này khi nhập vào ô input)
MOCK_EXAMPLE_HASH = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"

# Đây chính là "bảng dữ liệu ảo" bạn cần, lưu dưới dạng dictionary Python
MOCK_DATA = {
    # Dữ liệu giả cho trạng thái node
    "/heartbeat": {
        "data": {"code": 1, "type": 2, "message": "ok (Dữ liệu giả)"},
        "error": None
    },
    "/chain/height": {
        "data": {"height": 4012345}, # Chiều cao khối mẫu
        "error": None
    },
    "/node/info": {
        "data": {
            "node": { "protocol": "http", "host": "mock.nem.local", "port": 7890, },
            "nisInfo": {
                "currentTime": int(time.time() * 1000),
                "application": "NEM Infrastructure Server",
                "startTime": int((time.time() - 3600*24) * 1000), # Giả lập node chạy 1 ngày
                "version": "0.6.99-MOCK-VN", # Phiên bản giả
                "signer": None,
                "networkId": 104 # 104 là Mainnet, -104 là Testnet
            }
        },
        "error": None
    },
    # Dữ liệu giả cho tra cứu tài khoản (chỉ hoạt động với địa chỉ MOCK_EXAMPLE_ADDRESS)
    f"/account/get?address={MOCK_CLEANED_ADDRESS}": {
        "data": {
            "meta": {"cosignatories": [], "cosignatoryOf": [], "status": "LOCKED", "remoteStatus": "INACTIVE"},
            "account": {
                "address": MOCK_CLEANED_ADDRESS,
                "harvestedBlocks": 15,
                "balance": 123456789, # Số dư: 123.456789 XEM (đơn vị microXEM)
                "importance": 0.00012345,
                "vestedBalance": 100000000, # Số dư đã xác nhận: 100 XEM
                "publicKey": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2", # Public key mẫu (64 ký tự hex)
                "label": "Tài khoản Demo Giả",
                "multisigInfo": {}
            }
        },
        "error": None
    },
    # Dữ liệu giả cho tra cứu giao dịch (chỉ hoạt động với MOCK_EXAMPLE_HASH)
    f"/transaction/get?hash={MOCK_EXAMPLE_HASH}": {
        "data": {
            "meta": {
                "innerHash": {}, "id": 98765, "hash": {"data": MOCK_EXAMPLE_HASH}, "height": 4012300
            },
            "transaction": {
                "timeStamp": 195000000, # Thời gian NEM (giây tính từ block gốc)
                "amount": 50000000, # Số lượng: 50 XEM (microXEM)
                "signature": "f1e2d3c4b5a6f1e2d3c4b5a6f1e2d3c4b5a6f1e2d3c4b5a6f1e2d3c4b5a6f1e2d3c4b5a6f1e2d3c4", # Chữ ký mẫu (128 ký tự hex)
                "fee": 100000, # Phí: 0.1 XEM (microXEM)
                "recipient": "NBZDEE-37UHFG-QS3HEA-CQIP3W-XMYNP4-6HDPPA-Y2K4", # Địa chỉ người nhận mẫu
                "type": 257, # Loại giao dịch: Transfer (Chuyển khoản)
                "deadline": 195003600, # Hạn chót (NEM time)
                "message": {
                    # Hex của "Day la tin nhan giao dich gia."
                    "payload": "446179206c612074696e206e68616e206769616f2064696368206769612e",
                    "type": 1 # Loại tin nhắn: Plain (văn bản thường)
                },
                "version": 1744830465, # Version cho Mainnet (-1744830463 cho testnet)
                "signer": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2" # Public key người gửi (giống tài khoản mẫu)
            }
        },
        "error": None
    },
    # Dữ liệu lỗi giả khi không tìm thấy tài khoản
    "ERROR_ACCOUNT_NOT_FOUND": {
        "data": None,
        "error": "Lỗi API Giả: Không tìm thấy tài khoản được chỉ định."
    },
    # Dữ liệu lỗi giả khi không tìm thấy giao dịch
    "ERROR_TRANSACTION_NOT_FOUND": {
         "data": None,
         "error": "Lỗi API Giả: Mã hash giao dịch không tồn tại hoặc không hợp lệ."
    }
}

# --- Hàm lấy dữ liệu giả ---
def get_mock_data(endpoint, params=None):
    """Trả về dữ liệu giả dựa trên endpoint và tham số."""
    # Xử lý logic để trả về đúng dữ liệu giả dựa trên endpoint và params
    if endpoint == "/account/get":
        # Nếu tra cứu tài khoản, kiểm tra xem địa chỉ có khớp với địa chỉ mẫu không
        if params and params.get('address') == MOCK_CLEANED_ADDRESS:
            key = f"/account/get?address={MOCK_CLEANED_ADDRESS}"
            return MOCK_DATA[key]['data'], MOCK_DATA[key]['error']
        else:
            # Nếu không khớp, trả về lỗi giả "không tìm thấy"
            return MOCK_DATA["ERROR_ACCOUNT_NOT_FOUND"]['data'], MOCK_DATA["ERROR_ACCOUNT_NOT_FOUND"]['error']
    elif endpoint == "/transaction/get":
        # Nếu tra cứu giao dịch, kiểm tra xem hash có khớp với hash mẫu không
        lookup_hash = params.get('hash') or params.get('id') # Chấp nhận cả 'hash' và 'id'
        if params and lookup_hash == MOCK_EXAMPLE_HASH:
             key = f"/transaction/get?hash={MOCK_EXAMPLE_HASH}"
             return MOCK_DATA[key]['data'], MOCK_DATA[key]['error']
        else:
             # Nếu không khớp, trả về lỗi giả "không tìm thấy"
             return MOCK_DATA["ERROR_TRANSACTION_NOT_FOUND"]['data'], MOCK_DATA["ERROR_TRANSACTION_NOT_FOUND"]['error']
    elif endpoint in MOCK_DATA:
        # Nếu là các endpoint trạng thái node, trả về dữ liệu tương ứng
        return MOCK_DATA[endpoint]['data'], MOCK_DATA[endpoint]['error']
    else:
        # Nếu endpoint không được định nghĩa trong dữ liệu giả
        return None, f"Endpoint chưa được cấu hình dữ liệu giả: {endpoint}"

# --- Hàm lấy tên loại giao dịch ---
def get_transaction_type_name(tx_type):
    """Get human-readable name for NEM transaction type."""
    transaction_types = {
        257: "Transfer Transaction",
        258: "Importance Transfer Transaction",
        259: "Aggregate Modification Transaction",
        4097: "Provision Namespace Transaction",
        4098: "Mosaic Creation Transaction",
        4099: "Mosaic Supply Change Transaction",
        8193: "Account Key Link Transaction",
        8194: "Node Key Link Transaction",
        8195: "VRF Key Link Transaction",
        16385: "Account Metadata Transaction",
        16386: "Mosaic Metadata Transaction",
        16387: "Namespace Metadata Transaction",
        32769: "Account Address Restriction Transaction",
        32770: "Account Mosaic Restriction Transaction",
        32771: "Account Operation Restriction Transaction",
        32772: "Mosaic Address Restriction Transaction",
        32773: "Mosaic Global Restriction Transaction",
        65537: "Aggregate Complete Transaction",
        65538: "Aggregate Bonded Transaction",
        131073: "Lock Transaction",
        131074: "Secret Lock Transaction",
        131075: "Secret Proof Transaction",
        196609: "Account Property Transaction",
        262145: "Mosaic Definition Transaction",
        262146: "Mosaic Supply Change Transaction",
        524289: "Address Alias Transaction",
        524290: "Mosaic Alias Transaction",
        786433: "Account Restriction Transaction",
        1048577: "Mosaic Restriction Transaction",
        1310721: "Exchange Offer Transaction",
        1310722: "Exchange Withdrawal Transaction",
        1310723: "Exchange Deposit Transaction",
        1310724: "Exchange Cancel Transaction",
        1310725: "Exchange Claim Transaction"
    }
    return transaction_types.get(tx_type, "Unknown Transaction Type")

# --- Giao diện ứng dụng Streamlit ---
st.set_page_config(page_title="NEM (XEM) Mock Demo", layout="wide")

# Lấy thời gian hiện tại
current_time_utc = datetime.now(timezone.utc)
current_time_local = datetime.now()

st.title("🎓 Demo NEM (XEM) - Dữ liệu Giả")
st.caption(f"Hiển thị dữ liệu mẫu được định nghĩa sẵn. Thời gian hiện tại: {current_time_local.strftime('%Y-%m-%d %H:%M:%S')} (Local), {current_time_utc.strftime('%Y-%m-%d %H:%M:%S %Z')} (UTC)")
st.info("ℹ️ **Lưu ý:** Demo này sử dụng **dữ liệu giả** được lưu trữ sẵn trong code. Nó **không** kết nối đến mạng NEM thật. Hãy sử dụng các địa chỉ/hash mẫu được cung cấp để xem dữ liệu.")
st.markdown("---")

# --- Phần chọn Node (Đơn giản hóa vì là dữ liệu giả) ---
st.sidebar.header("Nguồn Dữ Liệu")
st.sidebar.success("🟢 Đang dùng Nguồn Dữ Liệu Giả (Mock)")
st.sidebar.markdown("Demo này không kết nối đến node NEM nào.")

# --- Các Tab hiển thị ---
tab1, tab2, tab3 = st.tabs(["📊 Trạng Thái Node (Giả)", "👤 Thông Tin Tài Khoản (Giả)", "📄 Tra Cứu Giao Dịch (Giả)"])

# --- Tab 1: Trạng Thái Node Giả ---
with tab1:
    st.subheader("Trạng Thái Node & Thông Tin Chuỗi (Giả)")
    if st.button("Hiển thị Trạng Thái Node Giả", key="check_node"):
        st.info("Đang tải dữ liệu trạng thái giả...")
        # Giả lập quá trình tải
        progress_bar = st.progress(0)
        status_area = st.empty()
        results = {}
        endpoints_to_check = {"Heartbeat": "/heartbeat", "Chain Height": "/chain/height", "Node Info": "/node/info"}
        total_checks = len(endpoints_to_check)

        for i, (name, endpoint) in enumerate(endpoints_to_check.items()):
            status_area.write(f"Đang lấy dữ liệu giả cho {name}...")
            data, error = get_mock_data(endpoint) # Gọi hàm lấy dữ liệu giả
            results[name] = {'data': data, 'error': error}
            progress_bar.progress((i + 1) / total_checks)
            time.sleep(0.2)

        status_area.success("Đã tải xong dữ liệu giả.")
        st.markdown("---"); st.subheader("Kết quả:")

        # Hiển thị kết quả giả
        hb_res = results["Heartbeat"]
        if hb_res['error']: st.error(f"💔 Lỗi Heartbeat giả: {hb_res['error']}")
        elif hb_res['data']: st.success(f"✅ Heartbeat Node Giả OK: {hb_res['data'].get('message')}")
        else: st.warning("❓ Không có dữ liệu heartbeat giả.")
        st.divider()

        height_res = results["Chain Height"]
        if height_res['error']: st.error(f"🧱 Lỗi Chiều Cao Chuỗi giả: {height_res['error']}")
        elif height_res['data']: st.success(f"⛓️ Chiều Cao Chuỗi Giả: **{height_res['data']['height']}**"); st.json(height_res['data'])
        else: st.warning("❓ Không có dữ liệu chiều cao chuỗi giả.")
        st.divider()

        nodeinfo_res = results["Node Info"]
        if nodeinfo_res['error']: st.error(f"ℹ️ Lỗi Thông Tin Node giả: {nodeinfo_res['error']}")
        elif nodeinfo_res['data']: st.info("Thông Tin Node Giả:"); st.json(nodeinfo_res['data']); st.success("✅ Đã hiển thị thông tin node giả.")
        else: st.warning("❓ Không có dữ liệu thông tin node giả.")


# --- Tab 2: Thông Tin Tài Khoản Giả ---
with tab2:
    st.subheader("Thông Tin Tài Khoản (Giả)")
    st.markdown(f"**Nhập địa chỉ ví mẫu sau để xem dữ liệu:** `{MOCK_EXAMPLE_ADDRESS}`")
    xem_address_input = st.text_input(
        "Nhập địa chỉ ví NEM",
        "",
        placeholder=f"Dán địa chỉ mẫu vào đây: {MOCK_EXAMPLE_ADDRESS}"
    ).strip().upper().replace("-", "") # Xóa dấu gạch ngang và chuyển thành chữ hoa

    if st.button("Xem Chi Tiết Tài Khoản Giả", key="get_account"):
        if not xem_address_input:
            st.warning("Vui lòng nhập địa chỉ ví NEM (sử dụng địa chỉ mẫu!).")
        else:
            st.info(f"Đang tìm dữ liệu giả cho địa chỉ: `{xem_address_input}`")
            with st.spinner("Đang tải dữ liệu giả..."):
                # Gọi hàm lấy dữ liệu giả cho tài khoản
                acc_data, acc_error = get_mock_data("/account/get", params={'address': xem_address_input})
                time.sleep(0.5) # Giả lập độ trễ

            if acc_error:
                st.error(f"❌ {acc_error}") # Hiển thị lỗi giả (nếu địa chỉ không khớp mẫu)
            elif acc_data and 'account' in acc_data:
                st.success(f"✅ Hiển thị dữ liệu giả cho Tài khoản: `{acc_data['account'].get('address', 'N/A')}`")
                # Phần hiển thị giống như trước, nhưng dùng dữ liệu giả
                account_info = acc_data['account']
                balance_micro = account_info.get('balance', 0)
                balance_xem = balance_micro / 1_000_000
                st.metric(label="Số dư (XEM)", value=f"{balance_xem:,.6f}")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Điểm Importance", value=f"{account_info.get('importance', 0):.8f}")
                    vested_micro = account_info.get('vestedBalance', 0)
                    vested_xem = vested_micro / 1_000_000
                    st.metric(label="Số dư Vested (XEM)", value=f"{vested_xem:,.6f}")
                with col2:
                    st.metric(label="Số khối đã Harvest", value=f"{account_info.get('harvestedBlocks', 0)}")
                st.text_area("Public Key", value=f"{account_info.get('publicKey', 'N/A')}", height=68, disabled=True)
                st.write(f"**Nhãn:** `{account_info.get('label', 'Không có')}`")
                with st.expander("Xem Dữ Liệu Thô (Giả)"):
                    st.json(acc_data)
            else:
                 st.error("Không thể lấy dữ liệu tài khoản giả hợp lệ.")

# --- Tab 3: Tra Cứu Giao Dịch Giả ---
with tab3:
    st.subheader("Tra Cứu Giao Dịch (Giả)")
    st.markdown(f"**Nhập mã hash giao dịch mẫu sau để xem dữ liệu:** `{MOCK_EXAMPLE_HASH}`")
    tx_hash_input = st.text_input("Nhập Mã Hash Giao Dịch", "", placeholder=f"Dán mã hash mẫu vào đây: {MOCK_EXAMPLE_HASH}").strip().lower()

    if st.button("Xem Chi Tiết Giao Dịch Giả", key="get_tx"):
        if not tx_hash_input:
            st.warning("Vui lòng nhập mã hash giao dịch (sử dụng mã mẫu!).")
        elif len(tx_hash_input) != 64: # Kiểm tra độ dài cơ bản
             st.warning("⚠️ Mã hash giao dịch thường có 64 ký tự hexa.")
        else:
            st.info(f"Đang tìm dữ liệu giả cho hash: `{tx_hash_input}`")
            with st.spinner("Đang tải dữ liệu giả..."):
                # Gọi hàm lấy dữ liệu giả cho giao dịch
                tx_data, tx_error = get_mock_data("/transaction/get", params={'hash': tx_hash_input})
                time.sleep(0.5) # Giả lập độ trễ

            if tx_error:
                st.error(f"❌ {tx_error}") # Hiển thị lỗi giả (nếu hash không khớp mẫu)
            elif tx_data and 'transaction' in tx_data and 'meta' in tx_data:
                meta_info = tx_data['meta']
                transaction_info = tx_data['transaction']
                display_hash = meta_info.get('hash', {}).get('data', tx_hash_input)
                st.success(f"✅ Hiển thị dữ liệu giả cho Giao dịch: `{display_hash}`")

                # Phần hiển thị giống như trước, dùng dữ liệu giả
                tx_type = transaction_info.get('type')
                st.write(f"**Loại:** `{tx_type}` ({get_transaction_type_name(tx_type)})")
                st.write(f"**Chiều cao khối:** `{meta_info.get('height', 'N/A')}`")

                nem_epoch_time = 1427587585 # Mốc thởi gian gốc của NEM Mainnet
                if 'timeStamp' in transaction_info:
                     nem_ts = transaction_info['timeStamp']
                     utc_ts = nem_ts + nem_epoch_time
                     st.write(f"**Thời gian (UTC):** `{datetime.utcfromtimestamp(utc_ts).strftime('%Y-%m-%d %H:%M:%S')} UTC`")

                signer_pk = transaction_info.get('signerPublicKey') or transaction_info.get('signer')
                st.text_area("Public Key Người Gửi", value=f"{signer_pk}", height=68, disabled=True)
                fee_micro = transaction_info.get('fee', 0)
                fee_xem = fee_micro / 1_000_000
                st.write(f"**Phí:** {fee_xem:,.6f} XEM ({fee_micro} microXEM)")

                st.markdown("---"); st.subheader("Chi tiết theo loại giao dịch:")
                if tx_type == 257: # Giao dịch chuyển khoản
                    recipient_addr = transaction_info.get('recipientAddress') or transaction_info.get('recipient')
                    st.write(f"**Địa chỉ người nhận:** `{recipient_addr}`")
                    amount_micro = transaction_info.get('amount', 0)
                    amount_xem = amount_micro / 1_000_000
                    st.write(f"**Số lượng:** {amount_xem:,.6f} XEM")
                    if 'message' in transaction_info and transaction_info['message'].get('payload'):
                        message_hex = transaction_info['message']['payload']
                        message_type = transaction_info['message'].get('type', 1)
                        if message_type == 1: # Tin nhắn thường
                            try: message_text = bytes.fromhex(message_hex).decode('utf-8', errors='replace'); st.text_area("Tin nhắn (Plain Text)", value=message_text, height=68, disabled=True)
                            except Exception: st.text_area("Tin nhắn (Hex)", value=message_hex, height=68, disabled=True); st.warning("Không thể giải mã tin nhắn UTF-8.")
                        else: st.text_area(f"Tin nhắn (Hex, Loại {message_type})", value=message_hex, height=68, disabled=True) # Tin nhắn mã hóa hoặc loại khác
                    else: st.write("**Tin nhắn:** *Không có*")
                else: st.info(f"Hiển thị thông tin chung cho loại giao dịch {tx_type}.")

                with st.expander("Xem Dữ Liệu Giao Dịch Thô (Giả)"):
                    st.json(tx_data)
            else:
                st.error("Không thể lấy dữ liệu giao dịch giả hợp lệ.")

st.markdown("---")
st.caption("Demo này chạy hoàn toàn trên máy tính của bạn bằng dữ liệu giả được định nghĩa sẵn. Nó mô phỏng cách một ứng dụng thật tương tác với blockchain NEM NIS1.")