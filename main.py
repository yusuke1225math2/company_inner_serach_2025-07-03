"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
# ログ出力を行うためのモジュール
import logging
import os

# streamlitアプリの表示を担当するモジュール
import streamlit as st

# （自作）画面表示系の関数が定義されているモジュール
import components as cn

# （自作）変数（定数）がまとめて定義・管理されているモジュール
import constants as ct

# （自作）画面表示以外の様々な関数が定義されているモジュール
import utils

# （自作）アプリ起動時に実行される初期化処理が記述された関数
from initialize import initialize

os.environ["USER_AGENT"] = "myagent"

############################################################
# 2. 設定関連
############################################################
# ブラウザタブの表示文言を設定
st.set_page_config(page_title=ct.APP_NAME)


# Streamlitコミュニティ対応のログ設定
def setup_streamlit_logger():
    """Streamlitコミュニティ対応のログ設定"""
    try:
        logger = logging.getLogger(ct.LOGGER_NAME)

        # すでにハンドラーが設定されている場合はスキップ
        if logger.hasHandlers():
            return logger

        # ログレベルを設定
        logger.setLevel(logging.INFO)

        # Streamlitのコンソールに出力するハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # フォーマッターを設定
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # ハンドラーをロガーに追加
        logger.addHandler(console_handler)

        return logger
    except Exception as e:
        st.error(f"ログ設定エラー: {e}")
        return None


# ログ出力を行うためのロガーの設定
logger = setup_streamlit_logger()


############################################################
# 3. 初期化処理
############################################################
try:
    # 初期化処理（「initialize.py」の「initialize」関数を実行）
    initialize()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()

# アプリ起動時のログファイルへの出力
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)


############################################################
# 4. 初期表示
############################################################
try:
    # タイトル表示
    cn.display_app_title()
    logger.info("タイトル表示完了")
except Exception as e:
    logger.error(f"タイトル表示エラー: {e}")
    st.error(f"タイトル表示に失敗しました: {e}")

try:
    # モード表示
    cn.display_select_mode()
    logger.info("モード表示完了")
except Exception as e:
    logger.error(f"モード表示エラー: {e}")
    st.error(f"モード表示に失敗しました: {e}")

try:
    # AIメッセージの初期表示
    cn.display_initial_ai_message()
    logger.info("AIメッセージ初期表示完了")
except Exception as e:
    logger.error(f"AIメッセージ初期表示エラー: {e}")
    st.error(f"AIメッセージ初期表示に失敗しました: {e}")


############################################################
# 5. 会話ログの表示
############################################################
try:
    # 会話ログの表示
    cn.display_conversation_log()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(
        utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON
    )
    # 後続の処理を中断
    st.stop()


############################################################
# 6. チャット入力の受け付け
############################################################
try:
    chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)
    if chat_message:
        logger.info(f"チャット入力受信: {chat_message[:50]}...")
except Exception as e:
    logger.error(f"チャット入力エラー: {e}")
    st.error(f"チャット入力に失敗しました: {e}")
    chat_message = None


############################################################
# 7. チャット送信時の処理
############################################################
if chat_message:
    try:
        # ==========================================
        # 7-1. ユーザーメッセージの表示
        # ==========================================
        # ユーザーメッセージのログ出力
        logger.info(
            f"ユーザーメッセージ: {chat_message[:50]}... (モード: {st.session_state.mode})"
        )

        # ユーザーメッセージを表示
        with st.chat_message("user"):
            st.markdown(chat_message)
        logger.info("ユーザーメッセージ表示完了")
    except Exception as e:
        logger.error(f"ユーザーメッセージ表示エラー: {e}")
        st.error(f"ユーザーメッセージ表示に失敗しました: {e}")

    try:
        # ==========================================
        # 7-2. LLMからの回答取得
        # ==========================================
        # 「st.spinner」でグルグル回っている間、表示の不具合が発生しないよう空のエリアを表示
        res_box = st.empty()
        # LLMによる回答生成（回答生成が完了するまでグルグル回す）
        with st.spinner(ct.SPINNER_TEXT):
            try:
                logger.info("LLM回答生成開始")
                # 画面読み込み時に作成したRetrieverを使い、Chainを実行
                llm_response = utils.get_llm_response(chat_message)
                logger.info("LLM回答生成完了")
            except Exception as e:
                # エラーログの出力
                logger.error(f"LLM回答生成エラー: {e}")
                # エラーメッセージの画面表示
                st.error(
                    utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE),
                    icon=ct.ERROR_ICON,
                )
                # 後続の処理を中断
                st.stop()
    except Exception as e:
        logger.error(f"LLM回答取得処理エラー: {e}")
        st.error(f"LLM回答取得処理に失敗しました: {e}")
        st.stop()

    try:
        # ==========================================
        # 7-3. LLMからの回答表示
        # ==========================================
        with st.chat_message("assistant"):
            try:
                # ==========================================
                # モードが「社内文書検索」の場合
                # ==========================================
                if st.session_state.mode == ct.ANSWER_MODE_1:
                    logger.info("社内文書検索モードで回答表示開始")
                    # 入力内容と関連性が高い社内文書のありかを表示
                    content = cn.display_search_llm_response(llm_response)
                    logger.info("社内文書検索モードで回答表示完了")

                # ==========================================
                # モードが「社内問い合わせ」の場合
                # ==========================================
                elif st.session_state.mode == ct.ANSWER_MODE_2:
                    logger.info("社内問い合わせモードで回答表示開始")
                    # 入力に対しての回答と、参照した文書のありかを表示
                    content = cn.display_contact_llm_response(llm_response)
                    logger.info("社内問い合わせモードで回答表示完了")

                # AIメッセージのログ出力
                logger.info(
                    f"AI回答: {content[:100]}... (モード: {st.session_state.mode})"
                )
            except Exception as e:
                # エラーログの出力
                logger.error(f"回答表示エラー: {e}")
                # エラーメッセージの画面表示
                st.error(
                    utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE),
                    icon=ct.ERROR_ICON,
                )
                # 後続の処理を中断
                st.stop()
    except Exception as e:
        logger.error(f"LLM回答表示処理エラー: {e}")
        st.error(f"LLM回答表示処理に失敗しました: {e}")
        st.stop()

    try:
        # ==========================================
        # 7-4. 会話ログへの追加
        # ==========================================
        # 表示用の会話ログにユーザーメッセージを追加
        st.session_state.messages.append({"role": "user", "content": chat_message})
        # 表示用の会話ログにAIメッセージを追加
        st.session_state.messages.append({"role": "assistant", "content": content})
        logger.info("会話ログへの追加完了")
    except Exception as e:
        logger.error(f"会話ログ追加エラー: {e}")
        st.error(f"会話ログの追加に失敗しました: {e}")
