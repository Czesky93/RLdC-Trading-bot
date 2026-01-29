# RLdC Repo Audit Report

Generated: 2026-01-29T22:38:24.392879+00:00

## Issues
- **missing_config_json** in `config_manager.py`: config.json referenced but not found in repo
- **missing_config_json** in `ai_code_auditor.py`: config.json referenced but not found in repo
- **missing_config_json** in `ultimate_ai.py`: config.json referenced but not found in repo
- **missing_config_json** in `rldc_quantum_ai.py`: config.json referenced but not found in repo
- **missing_config_json** in `installer.py`: config.json referenced but not found in repo
- **missing_config_json** in `news_watcher.py`: config.json referenced but not found in repo
- **missing_config_json** in `blockchain_analysis.py`: config.json referenced but not found in repo
- **missing_config_json** in `binance_trader.py`: config.json referenced but not found in repo
- **missing_config_json** in `zordon_ai.py`: config.json referenced but not found in repo
- **missing_config_json** in `telegram_bot.py`: config.json referenced but not found in repo
- **missing_config_json** in `auto_trader.py`: config.json referenced but not found in repo
- **missing_config_json** in `telegram_ai_bot.py`: config.json referenced but not found in repo
- **missing_imports** in `whale_tracker.py`: ['os']
- **missing_config_json** in `whale_tracker.py`: config.json referenced but not found in repo
- **missing_config_json** in `web_portal.py`: config.json referenced but not found in repo
- **missing_config_json** in `master_ai_trader.py`: config.json referenced but not found in repo
- **missing_config_json** in `web_interface.py`: config.json referenced but not found in repo
- **missing_config_json** in `gpt_market_analysis.py`: config.json referenced but not found in repo
- **missing_config_json** in `ai_settings.py`: config.json referenced but not found in repo
- **missing_config_json** in `ai_optimizer.py`: config.json referenced but not found in repo
- **missing_config_json** in `demo_trading.py`: config.json referenced but not found in repo
- **missing_config_json** in `rldc_manager.py`: config.json referenced but not found in repo
- **missing_config_json** in `trading/binance_api.py`: config.json referenced but not found in repo
- **placeholder_tokens** in `backend/notifications.py`: ['your_email@example.com', 'your_password']
- **placeholder_tokens** in `auth/oauth.py`: ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']

## Top-level calls (possible side effects on import)
- `app.py`: db.init_app(app)
- `ai_automl.py`: optimize_strategy('BTCUSDT')
- `news_watcher.py`: auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
- `ai_analyzer.py`: print(f'📈 AI rekomenduje: {analyze_market()}')
- `trading_strategy.py`: print(f'💰 Strategia EMA: {get_trading_signal()}')
- `telegram_ai_bot.py`: bot.message_loop(handle_message), print('✅ Telegram AI Bot działa!'), send_telegram_message('🚀 RLdC Trading Bot aktywowany!')
- `whale_tracker.py`: track_whale_activity('BTCUSDT')
- `rldc_manager.py`: os.makedirs(LOG_DIR, exist_ok=True)
- `rldc_analyzer_backend.py`: os.makedirs(LOG_DIR, exist_ok=True)
- `modules/analysis/setup.py`: setup(name='analysis_module', version='1.0.0', packages=find_packages(), entry_points={'console_scripts': ['analysis=analysis.analysis:analysis_function']})
- `modules/trading/setup.py`: setup(name='trading_module', version='1.0.0', packages=find_packages(), entry_points={'console_scripts': ['trading=trading.trading:trading_function']})
- `modules/registration/setup.py`: setup(name='registration_module', version='1.0.0', packages=find_packages(), entry_points={'console_scripts': ['registration=registration.registration:registration_function']})