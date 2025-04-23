# Corrected Code (Adds import datetime)
import streamlit as st
import time
import random # Keep random for placeholder data where SDK calls fail/are not implemented
import string # Needed for mock key generation if SDK fails
import datetime # <<< FIXED: Added missing import

st.set_page_config(page_title="NEM (XEM) Testnet Demo", layout="wide")

# --- !!! SDK PLACEHOLDER !!! ---
# You would need to install a NEM NIS1 Python SDK, e.g., pip install nem-python-kit (if available/working)
# Then import the necessary classes. The names below are *examples*.
try:
    # --- Replace with actual SDK imports ---
    from nem_sdk import NemClient, KeyPair, Transaction, NetworkType, NodeSelector, Address
    from nem_sdk.models import TransferTransaction, PlainMessage
    from nem_sdk.network import NetworkConfig
    # --- End Replace ---
    SDK_AVAILABLE = True
except ImportError:
    st.sidebar.error("⚠️ NEM NIS1 SDK not found. Please install a suitable library (e.g., 'nem-python-kit') and adjust imports. Running in limited mock mode.")
    SDK_AVAILABLE = False
    # Define dummy classes/functions if SDK is missing, to prevent NameErrors
    class KeyPair:
        @staticmethod
        def generate(): return KeyPair()
        def __init__(self):
            self.private_key = "mock_private_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=64))
            self.public_key = "mock_public_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=64))
        def get_address(self, net_type): return "T" + "MOCKADDRESS" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=30))
        def sign(self, tx): return "signed_mock_tx_payload"
    class NemClient:
        def __init__(self, url): self.url = url
        def get_account_info(self, addr): return {"balance": random.randint(0, 1000) * 1000000} # Mock microXem
        def announce_transaction(self, signed_tx): return {"transactionHash": "mock_tx_hash_" + ''.join(random.choices(string.hexdigits, k=64))}
        def get_account_transactions(self, addr, direction='all'): return [] # Mock history
    class TransferTransaction:
        @staticmethod
        def create(*args, **kwargs): return "mock_tx_object"
    class PlainMessage:
        def __init__(self, msg): self.message = msg
    class NetworkType:
        TEST_NET = 152 # Example value for testnet identifier
    class Address:
        def __init__(self, addr): self.plain = addr
        def is_valid(self): return isinstance(self.plain, str) and len(self.plain) > 30 and self.plain.startswith("T") # Basic mock validation
# --- END SDK PLACEHOLDER ---


# --- Configuration ---
# Find public NEM Testnet node URLs (search online for "NEM NIS1 Testnet nodes")
# Example list, check for currently active ones!
# TESTNET_NODE_URLS = [
#     "http://bob.nem.ninja:7778", # Often used NIS testnet nodes
#     "http://104.128.226.60:7890",
#     "http://23.228.67.85:7890",
# ]
# Using a single reliable one for simplicity in the demo:
DEFAULT_TESTNET_NODE = "http://bob.nem.ninja:7778" # CHECK IF THIS IS ACTIVE!
NEM_EPOCH = datetime.datetime(2015, 3, 29, 0, 6, 25, tzinfo=datetime.timezone.utc)


# --- SDK Helper Functions (Adapt based on actual SDK) ---
def generate_testnet_account():
    """Generate a new NEM Testnet account."""
    # Generate a random private key (32 bytes)
    private_key = ''.join(random.choices(string.hexdigits.lower(), k=64))
    # Public key is derived from private key (mock implementation)
    public_key = ''.join(random.choices(string.hexdigits.lower(), k=64))
    # Address format: T- followed by 39 characters (mock implementation)
    address = f"T-{''.join(random.choices(string.ascii_uppercase + string.digits, k=39))}"
    
    return {
        "private_key": private_key,
        "public_key": public_key,
        "address": address
    }

def get_account_balance(address):
    """Get account balance (mock implementation)."""
    # In real implementation, this would query the NEM Testnet node
    return random.randint(0, 1000000)  # Return random balance for demo

@st.cache_resource # Cache the client connection per node URL
def get_nem_client(node_url):
    if not SDK_AVAILABLE:
        # st.warning("SDK not available, using mock client.") # Warning moved to sidebar
        return NemClient(node_url) # Return mock client
    try:
        # --- Replace with actual SDK client initialization ---
        client = NemClient(node_url)
        # Perform a basic check if possible, e.g., get node info
        # client.get_node_info()
        # --- End Replace ---
        return client
    except Exception as e:
        st.error(f"Failed to connect to node {node_url}: {e}")
        return None

def generate_testnet_account_sdk():
    if not SDK_AVAILABLE: return KeyPair().generate() # Use mock KeyPair
    # --- Replace with actual SDK key generation ---
    key_pair = KeyPair.generate()
    # --- End Replace ---
    return key_pair

@st.cache_data(ttl=60) # Cache balance for 60 seconds
def get_account_balance_sdk(_client, address_str): # _client arg helps caching trigger
    if not SDK_AVAILABLE or _client is None: return 0.0
    try:
        client = _client # Avoid modifying the cached client object directly if needed
        address_obj = Address(address_str) # Create address object
        if not address_obj.is_valid(): # Check validity before SDK call
            # st.warning(f"Invalid address format for balance check: {address_str[:8]}...", icon="⚠️")
            return 0.0
        # --- Replace with actual SDK balance check ---
        account_info = client.get_account_info(address_obj) # Pass address object
        balance_micro_xem = account_info['balance'] # Adjust based on actual SDK return structure
        # --- End Replace ---
        return balance_micro_xem / 1_000_000.0 # Convert from microXEM to XEM
    except Exception as e:
        # Handle accounts not found (zero balance) vs other errors
        if "does not exist" in str(e).lower() or "account_not_found" in str(e).upper():
             return 0.0
        st.warning(f"Could not get balance for {address_str[:8]}...: {e}", icon="⚠️")
        return 0.0 # Return 0 on error

def send_transaction_sdk(client, key_pair, recipient_address_str, amount_xem, message_str=""):
    if not SDK_AVAILABLE or client is None:
        st.error("SDK not available or client not connected.")
        return None, "SDK Error"
    try:
        sender_address = key_pair.get_address(NetworkType.TEST_NET) # Get sender addr from keys
        recipient_address = Address(recipient_address_str)

        # --- Input validation ---
        if not recipient_address.is_valid(): # Use SDK's validation
             return None, "Invalid recipient address format."
        if amount_xem <= 0:
            return None, "Amount must be positive."
        # Basic check if sender has *any* balance - more precise check done by network/SDK
        # current_balance = get_account_balance_sdk(client, sender_address) # Careful with caching here if needed immediately
        # if current_balance < amount_xem: # Doesn't account for fee accurately here
        #    return None, "Insufficient balance (pre-check, fee not included)."

        # --- Replace with actual SDK transaction creation ---
        tx = TransferTransaction.create(
            network_type=NetworkType.TEST_NET, # Make sure SDK uses this constant
            recipient_address=recipient_address, # Pass address object
            amount=int(amount_xem * 1_000_000), # Use microXEM
            message=PlainMessage(message_str) if message_str else None
        )
        # SDK might calculate fees automatically, or you might need to set it.
        # tx.fee = calculate_fee(tx) # Example if manual calc needed

        signed_tx = key_pair.sign(tx)
        response = client.announce_transaction(signed_tx)
        tx_hash = response['transactionHash'] # Adjust based on actual SDK return structure
        # --- End Replace ---

        return tx_hash, None # Return hash on success, None for error message
    except Exception as e:
        st.error(f"Transaction failed: {e}")
        return None, str(e)

@st.cache_data(ttl=120) # Cache history for 2 minutes
def get_transaction_history_sdk(_client, address_str):
    if not SDK_AVAILABLE or _client is None: return []
    try:
        client = _client
        address_obj = Address(address_str) # Create address object
        if not address_obj.is_valid(): # Check validity
             return []
        # --- Replace with actual SDK history fetch ---
        # Note: SDKs often return complex objects. You'll need to parse them.
        # This might fetch incoming, outgoing, or all. Check SDK docs.
        transactions = client.get_account_transactions(address_obj, direction='all') # Example
        # --- End Replace ---

        # --- Basic Parsing Example (ADAPT TO YOUR SDK's return format) ---
        parsed_history = []
        for tx in transactions:
             # This is highly dependent on the SDK's transaction object structure
             tx_data = {}
             try:
                 # Use getattr for safety in case attributes are missing in some tx types
                 tx_data['hash'] = getattr(tx, 'hash', 'N/A')
                 tx_data['type'] = getattr(tx, 'type', 'N/A')
                 tx_data['sender'] = getattr(getattr(getattr(tx, 'signer', None), 'address', None), 'plain', 'N/A')
                 tx_data['recipient'] = getattr(getattr(tx, 'recipient', None), 'plain', 'N/A')
                 tx_data['amount'] = getattr(tx, 'amount', 0) / 1000000.0 # Amount in XEM
                 tx_data['fee'] = getattr(tx, 'fee', 0) / 1000000.0 # Fee in XEM
                 # Timestamps might need conversion from NEM epoch
                 nem_timestamp = getattr(tx, 'timestamp', None) # Or tx.transaction_info.timestamp
                 if nem_timestamp is not None:
                      tx_data['timestamp'] = NEM_EPOCH + datetime.timedelta(seconds=nem_timestamp)
                 else:
                      tx_data['timestamp'] = datetime.datetime.now(datetime.timezone.utc) # Fallback timestamp

                 message_obj = getattr(tx, 'message', None)
                 tx_data['message'] = getattr(message_obj, 'payload', '') if message_obj else '' # Extract message payload

                 parsed_history.append(tx_data)
             except Exception as e: # Catch broader exceptions during parsing
                 st.warning(f"Skipping transaction due to parsing error: {e}", icon="⚠️")
                 continue # Skip transactions that don't fit the expected structure
        return parsed_history
        # --- End Basic Parsing Example ---

    except Exception as e:
        st.error(f"Failed to get transaction history: {e}")
        return []


# --- Streamlit App ---
st.title(" Krypto NEM (XEM) Testnet Interaction Demo")
st.caption("Interacts with the **NEM Testnet**. Transactions are real but use valueless test XEM.")
st.warning("⚠️ **Security Risk:** Never enter real mainnet private keys here. Testnet keys generated are stored temporarily in session state for convenience, which is insecure for real applications.")
st.markdown("---")

# --- Initialize Session State ---
if 'accounts' not in st.session_state:
    st.session_state.accounts = [] # Stores dicts: {"address": str, "public_key": str, "key_pair": KeyPair_object} - **Storing KeyPair is insecure!**
if 'selected_address' not in st.session_state:
    st.session_state.selected_address = None
if 'selected_node' not in st.session_state:
     st.session_state.selected_node = DEFAULT_TESTNET_NODE

# --- Sidebar ---
with st.sidebar:
    st.header("Network")
    st.session_state.selected_node = st.text_input("Testnet Node URL", st.session_state.selected_node)
    # Get client only once per run based on selected node
    client = get_nem_client(st.session_state.selected_node)

    if client and SDK_AVAILABLE: # Only show success if SDK is loaded and client initialized
         # Add a more concrete check if possible with your SDK, e.g. fetching node time
         try:
              # node_time = client.get_node_time() # Example SDK call
              st.success(f"🟢 Connected (Client initialized for {st.session_state.selected_node})")
         except Exception as e:
              st.error(f"🔴 Node Check Failed: {e}")
              client = None # Invalidate client if check fails
    elif SDK_AVAILABLE and not client:
        st.error("🔴 Connection failed. Check Node URL or network.")
    # If SDK not available, the error is shown during import time

    st.markdown("---")
    st.header("Testnet Accounts")
    st.info("ℹ️ Get free Testnet XEM from a [NEM Testnet Faucet](https://nemfaucet.utazukin.com/) (external link, search for others if down).")


    if st.button("🔑 Generate New Testnet Account"):
        if not SDK_AVAILABLE:
            st.error("Cannot generate account without SDK.")
        else:
             with st.spinner("Generating keys..."):
                 account = generate_testnet_account()
                 new_account_data = {
                     "address": account['address'],
                     "public_key": account['public_key'],
                     "private_key": account['private_key']
                 }
                 st.session_state.accounts.append(new_account_data)
                 st.session_state.selected_address = account['address']
                 st.success(f"Generated Account: {account['address'][:8]}...")
                 st.code(f"Address: {account['address']}\nPublic Key: {account['public_key']}\nPrivate Key: {account['private_key']}\n\n--- !!! SAVE PRIVATE KEY SECURELY !!! ---", language=None)
                 # Don't rerun here, allow user to copy the key first
                 # st.rerun() # Removed rerun


    if st.session_state.accounts:
        account_options = {acc["address"]: f"{acc['address'][:8]}..." for acc in st.session_state.accounts}
        current_selection_index = 0
        # Safely get the current selection index
        if st.session_state.selected_address in account_options:
            current_selection_index = list(account_options.keys()).index(st.session_state.selected_address)
        else:
             # If selected address is no longer valid (e.g., state reset issue), default to first
             if account_options:
                  st.session_state.selected_address = list(account_options.keys())[0]
                  current_selection_index = 0
             else: # No accounts exist
                 st.session_state.selected_address = None


        selected_key = st.selectbox(
            "Select Account:",
            options=list(account_options.keys()),
            format_func=lambda x: account_options.get(x, "N/A"), # Use .get for safety
            index=current_selection_index,
            key="account_selector_real"
        )
        # Update state only if selection changed
        if selected_key != st.session_state.selected_address:
             st.session_state.selected_address = selected_key
             # Clear caches when account changes, forces refresh of balance/history for new account
             get_account_balance_sdk.clear()
             get_transaction_history_sdk.clear()
             st.rerun() # Rerun immediately on selection change
    else:
        st.write("No testnet accounts generated yet.")

# --- Main Area ---
selected_account_data = None
selected_key_pair = None # Store the keypair object for the selected account
if st.session_state.selected_address:
    for acc in st.session_state.accounts:
        if acc["address"] == st.session_state.selected_address:
            selected_account_data = acc
            # selected_key_pair = acc.get("key_pair") # Use .get for safety
            break

if not selected_account_data or not client:
    if not client and SDK_AVAILABLE:
        st.error("🔴 Cannot proceed: Failed to connect to the selected Testnet node. Please check the URL and your connection.")
    else:
        st.info("👈 Please select/generate an account and ensure a valid Testnet Node is entered in the sidebar.")

else:
    # Make sure key_pair is loaded if account is selected (handle potential state loss)
    if not selected_key_pair:
        st.error("⚠️ Critical Error: Key pair for selected account is missing from session state. Please regenerate the account.")
    else:
        tab1, tab2, tab3 = st.tabs(["📊 Account Info", "💸 Send Testnet XEM", "📜 Transaction History"])

        with tab1:
            st.subheader(f"Account Details: `{selected_account_data['address'][:8]}...`")
            address = selected_account_data['address']
            st.code(f"Full Address: {address}", language=None)
            st.code(f"Public Key: {selected_account_data['public_key']}", language=None)
            st.info(f"ℹ️ To receive funds, use the address above. Fund via a [Testnet Faucet](https://nemfaucet.utazukin.com/).")

            st.markdown("---")
            st.subheader("Balance")
            if st.button("🔄 Refresh Balance", key="refresh_balance_btn"):
                # Clear cache for this specific account before fetching
                 get_account_balance_sdk.clear()

            # Fetch and display balance
            balance = get_account_balance(address) # Pass client for caching check
            st.metric("Balance (Testnet XEM)", f"{balance:.6f}")
            if balance == 0 and SDK_AVAILABLE: # Only show warning if SDK is supposed to be working
                 st.warning("Account might be empty or not yet seen by the network. Fund it via a Faucet.")

        with tab2:
            st.subheader("Create Testnet Transaction")

            # Allow sending to any address (must be validated by SDK/network)
            recipient_address_input = st.text_input("Recipient Testnet Address (starts with T)")
            amount_to_send = st.number_input("Amount (Testnet XEM)", min_value=0.000001, step=0.1, format="%.6f")
            message_input = st.text_input("Message (Optional)")

            st.caption("Transaction fees will be deducted automatically by the network.")

            if st.button("🚀 Send Testnet XEM", key="send_xem_btn"):
                if not selected_key_pair:
                     st.error("❌ Cannot send: Selected account's key pair not found.")
                elif not recipient_address_input:
                     st.error("❌ Please enter a recipient address.")
                elif amount_to_send <= 0:
                     st.error("❌ Please enter a positive amount.")
                else:
                    with st.spinner("📡 Preparing and sending transaction to Testnet..."):
                        tx_hash, error_msg = send_transaction_sdk(
                            client,
                            selected_key_pair, # Send the keypair object
                            recipient_address_input,
                            amount_to_send,
                            message_input
                        )

                    if tx_hash:
                        st.success(f"✅ Transaction announced to the network!")
                        st.caption("It may take a minute or two to confirm.")
                        st.code(f"Transaction Hash: {tx_hash}", language=None)
                        # Provide link to a Testnet explorer (replace with a real one if known)
                        explorer_url = f"http://bob.nem.ninja:8765/transaction/{tx_hash}" # Example explorer, CHECK IF VALID
                        st.markdown(f"[View on Testnet Explorer (Example Link)]({explorer_url})", unsafe_allow_html=True)
                        st.balloons()
                        # Clear balance cache after sending TO update UI potentially faster
                        # It won't reflect instantly, but next refresh will be sooner
                        get_account_balance_sdk.clear()
                        get_transaction_history_sdk.clear() # Also clear history cache
                    else:
                        st.error(f"❌ Transaction Failed: {error_msg}")

        with tab3:
            st.subheader("Testnet Transaction History")
            address = selected_account_data['address']

            if st.button("🔄 Refresh History", key="refresh_history_btn"):
                 get_transaction_history_sdk.clear()

            # Fetch and display history
            history = get_transaction_history_sdk(client, address)

            if not history:
                st.info("No transaction history found for this account on the selected node, or account is new.")
            else:
                st.write(f"Found {len(history)} transactions (showing latest):")
                for tx in history[:20]: # Show latest 20 to avoid clutter
                    ts_str = tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC') if isinstance(tx.get('timestamp'), datetime.datetime) else 'N/A'
                    tx_hash_short = str(tx.get('hash', 'N/A'))[:8] + "..." + str(tx.get('hash', 'N/A'))[-4:] if tx.get('hash') != 'N/A' else 'N/A'
                    explorer_link = f"http://bob.nem.ninja:8765/transaction/{tx.get('hash', '')}" # Example explorer

                    # Determine direction
                    direction_info = ""
                    if tx.get("sender") == address:
                        direction_info = f"➖ **Sent:** `{tx.get('amount', 0):.4f}` XEM to `{str(tx.get('recipient', 'N/A'))[:8]}...`"
                    elif tx.get("recipient") == address:
                         direction_info = f"➕ **Received:** `{tx.get('amount', 0):.4f}` XEM from `{str(tx.get('sender', 'N/A'))[:8]}...`"
                    else: # Should not happen if filtered correctly by SDK, but good to have a fallback
                         direction_info = f"ℹ️ **Other:** Type `{tx.get('type', 'N/A')}` involving this address."

                    # Construct display string
                    st.markdown(direction_info)
                    st.caption(f"   *Time:* {ts_str} | *Fee:* {tx.get('fee', 0):.4f} XEM | *Hash:* [{tx_hash_short}]({explorer_link})")

                    if tx.get('message'):
                         # Use st.text or st.code for message to prevent markdown interpretation
                         st.code(f"   Message: {tx['message']}", language=None)
                    st.markdown("---") # Separator