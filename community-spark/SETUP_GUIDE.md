# Community Spark - Quick Setup Guide

## ✅ What's Working

- ✅ Windows Hello passkey registration and sign-in
- ✅ Plaid sandbox integration with transaction data
- ✅ Multi-agent loan evaluation system
- ✅ Streamlit UI for loan applications
- ✅ WebAuthn passwordless authentication

## 🔧 Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Your API Keys

You need to set these environment variables. You can use 1Password (`op run`) or a `.env` file:

**Required:**
- `PLAID_CLIENT_ID` - From https://dashboard.plaid.com/team/keys (Sandbox)
- `PLAID_SECRET` - From https://dashboard.plaid.com/team/keys (Sandbox)
- `PASSKEY_HMAC_SECRET` - Any secure random string (e.g., `openssl rand -hex 32`)

**Optional but Recommended:**
- `OPENAI_API_KEY` - From https://platform.openai.com/api-keys
  - Enables LLM-enhanced agent reasoning (uses GPT-4o-mini)
  - Without it, agents use basic deterministic summaries

**Example `.env` file:**
```env
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=sandbox
PASSKEY_HMAC_SECRET=your_random_secret_here
OPENAI_API_KEY=sk-your_openai_key_here
```

### 3. Start the FastAPI Server

```bash
# With 1Password:
op run -- uvicorn app.main:app --reload

# Or without:
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000` (or `http://127.0.0.1:8000`)

### 4. Start the Streamlit UI (Optional)

In a separate terminal:

```bash
streamlit run streamlit_app.py
```

UI runs at: `http://localhost:8501`

## 🔐 WebAuthn / Passkeys

### Registration & Sign-In

1. Go to `http://localhost:8000/passkeys` (or `http://127.0.0.1:8000/passkeys`)
2. Enter a user ID (e.g., `user123`)
3. Click "Register Passkey"
4. Choose:
   - **Windows Hello** (works ✅)
   - **1Password** (may not work - see known issues)
   - **Security Key** (if you have one)
5. Click "Sign In / Approve Loan" to get an `assertion_token`
6. Use the token in Streamlit to finalize loan evaluations

### Known Issues

- ❌ **1Password passkeys may not work** - This is a known limitation with the current setup. Use Windows Hello instead.
- ✅ **Windows Hello works perfectly** - Use this for testing

## 💰 Plaid Mock Transaction Data

### Default Behavior

The `/evaluate/plaid` endpoint automatically uses **Tartan Bank** (institution ID: `ins_109509`), which has more transactions than the default bank.

### View Available Data

Run this script to see what transaction data is available:

```bash
op run -- python scripts/setup_plaid_mock_data.py
```

This will show you:
- Available accounts
- Sample transactions
- Transaction counts

### Plaid Sandbox Institutions

- `ins_109508`: First Platypus Bank (minimal transactions)
- `ins_109509`: Tartan Bank (MORE transactions - **default**)
- `ins_109510`: Houndstooth Bank (different patterns)

## 🤖 OpenAI Integration

### How It Works

When `OPENAI_API_KEY` is set, the agents use GPT-4o-mini to generate:
- **Auditor**: Detailed financial analysis summaries
- **Impact Analyst**: Community impact explanations
- **Compliance Sentry**: Clear decision rationales

### Without OpenAI

If the API key is not set, agents fall back to basic deterministic summaries. The system still works, but the explanations are less detailed.

### Cost

GPT-4o-mini is very cost-effective:
- ~$0.00015 per agent call
- ~$0.00045 per full evaluation (3 agents)

## 📊 API Endpoints

### Main Endpoints

- `GET /` - Welcome page
- `GET /health` - Health check
- `GET /secrets-check` - Check which secrets are configured (demo only)
- `POST /evaluate` - Evaluate with manual bank data
- `POST /evaluate/plaid` - Evaluate with Plaid sandbox data
- `POST /finalize` - Finalize evaluation with passkey signature
- `GET /passkeys` - WebAuthn registration/sign-in page

### WebAuthn Endpoints

- `POST /webauthn/register/options` - Get registration options
- `POST /webauthn/register/verify` - Verify registration
- `POST /webauthn/authenticate/options` - Get authentication options
- `POST /webauthn/authenticate/verify` - Verify authentication

## 🎯 Testing the Full Flow

### 1. Register a Passkey

```bash
# Open in browser:
http://localhost:8000/passkeys

# Register with Windows Hello
# User ID: user123
# Email: test@example.com
```

### 2. Run a Loan Evaluation

```bash
# Open Streamlit UI:
http://localhost:8501

# Fill in business profile:
# - Business name: Joe's Grocery
# - Type: grocery
# - Zip code: 10451
# - Hires locally: Yes

# Click "Run Evaluation"
```

### 3. Sign the Evaluation

```bash
# In the passkeys page:
http://localhost:8000/passkeys

# Click "Sign In / Approve Loan"
# Copy the assertion_token

# In Streamlit sidebar:
# Paste the token and click "Finalize Evaluation"
```

## 🐛 Troubleshooting

### "Credential not found" error

- Make sure you're using the same `user_id` for registration and sign-in
- Check the server console for debug logs showing credential IDs

### "No transactions" from Plaid

- The system now uses Tartan Bank by default, which has more transactions
- Wait a few seconds after creating a sandbox item (retry logic is built-in)

### 1Password passkeys don't work

- Known issue - use Windows Hello instead
- Or try a different `user_id` (1Password may have cached credentials)

### OpenAI API errors

- Check that `OPENAI_API_KEY` is set correctly
- The system will fall back to basic summaries if OpenAI fails
- Check the server console for `[WARNING] OpenAI API call failed` messages

## 📝 Next Steps

1. ✅ Set up your API keys
2. ✅ Start the server
3. ✅ Register a passkey with Windows Hello
4. ✅ Run a loan evaluation in Streamlit
5. ✅ Sign the evaluation with your passkey

Enjoy using Community Spark! 🎉

