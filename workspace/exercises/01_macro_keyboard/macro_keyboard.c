#include "ch32fun.h"
#include "rv003usb.h"

/* -------------------------------------------------------------------------
 * 初心者向けカスタマイズ設定
 * ------------------------------------------------------------------------- */

/* ロータリーエンコーダーモジュールのKEYを接続する端子です。 */
#define ENCODER_KEY_PIN PC3

/* スイッチのチャタリングを無視する時間です。通常は変更不要です。 */
#define DEBOUNCE_MS 20u

/* このモジュールのKEYは、押すとGNDにつながるためLowが押下状態です。 */
#define KEY_PRESSED_LEVEL FUN_LOW

/*
 * メタキー（修飾キー）
 * 複数を同時に使う場合は、MOD_CTRL | MOD_SHIFT のように | でつなぎます。
 */
#define MOD_NONE        0x00u
#define MOD_LEFT_CTRL   0x01u
#define MOD_LEFT_SHIFT  0x02u
#define MOD_LEFT_ALT    0x04u
#define MOD_LEFT_GUI    0x08u
#define MOD_RIGHT_CTRL  0x10u
#define MOD_RIGHT_SHIFT 0x20u
#define MOD_RIGHT_ALT   0x40u
#define MOD_RIGHT_GUI   0x80u

/* OSで呼び方が違うキーの、分かりやすい別名です。 */
#define MOD_CTRL    MOD_LEFT_CTRL   /* Windows/macOSのControlキー */
#define MOD_SHIFT   MOD_LEFT_SHIFT  /* Shiftキー */
#define MOD_ALT     MOD_LEFT_ALT    /* WindowsのAltキー */
#define MOD_OPTION  MOD_LEFT_ALT    /* macOSのOptionキー */
#define MOD_WIN     MOD_LEFT_GUI    /* Windowsキー */
#define MOD_COMMAND MOD_LEFT_GUI    /* macOSのCommandキー */

/* 通常キー: アルファベット */
#define KEY_NONE 0x00u
#define KEY_A    0x04u
#define KEY_B    0x05u
#define KEY_C    0x06u
#define KEY_D    0x07u
#define KEY_E    0x08u
#define KEY_F    0x09u
#define KEY_G    0x0Au
#define KEY_H    0x0Bu
#define KEY_I    0x0Cu
#define KEY_J    0x0Du
#define KEY_K    0x0Eu
#define KEY_L    0x0Fu
#define KEY_M    0x10u
#define KEY_N    0x11u
#define KEY_O    0x12u
#define KEY_P    0x13u
#define KEY_Q    0x14u
#define KEY_R    0x15u
#define KEY_S    0x16u
#define KEY_T    0x17u
#define KEY_U    0x18u
#define KEY_V    0x19u
#define KEY_W    0x1Au
#define KEY_X    0x1Bu
#define KEY_Y    0x1Cu
#define KEY_Z    0x1Du

/* 通常キー: 数字。Shiftとの組み合わせで記号になるキーもあります。 */
#define KEY_1 0x1Eu
#define KEY_2 0x1Fu
#define KEY_3 0x20u
#define KEY_4 0x21u
#define KEY_5 0x22u
#define KEY_6 0x23u
#define KEY_7 0x24u
#define KEY_8 0x25u
#define KEY_9 0x26u
#define KEY_0 0x27u

/* 通常キー: 編集、空白、記号 */
#define KEY_ENTER         0x28u
#define KEY_ESCAPE        0x29u
#define KEY_BACKSPACE     0x2Au
#define KEY_TAB           0x2Bu
#define KEY_SPACE         0x2Cu
#define KEY_MINUS         0x2Du
#define KEY_EQUAL         0x2Eu
#define KEY_LEFT_BRACKET  0x2Fu
#define KEY_RIGHT_BRACKET 0x30u
#define KEY_BACKSLASH     0x31u
#define KEY_SEMICOLON     0x33u
#define KEY_APOSTROPHE    0x34u
#define KEY_GRAVE         0x35u
#define KEY_COMMA         0x36u
#define KEY_PERIOD        0x37u
#define KEY_SLASH         0x38u
#define KEY_CAPS_LOCK     0x39u

/*
 * KEY_EQUALなどの記号キーは、USB HIDでは物理的なキー位置を表します。
 * 実際に入力される記号は、PC側の日本語/英語キーボード設定で変わります。
 */

/* ファンクションキー: F1～F12 */
#define KEY_F1  0x3Au
#define KEY_F2  0x3Bu
#define KEY_F3  0x3Cu
#define KEY_F4  0x3Du
#define KEY_F5  0x3Eu
#define KEY_F6  0x3Fu
#define KEY_F7  0x40u
#define KEY_F8  0x41u
#define KEY_F9  0x42u
#define KEY_F10 0x43u
#define KEY_F11 0x44u
#define KEY_F12 0x45u

/* 通常キー: 画面操作、移動 */
#define KEY_PRINT_SCREEN 0x46u
#define KEY_SCROLL_LOCK  0x47u
#define KEY_PAUSE        0x48u
#define KEY_INSERT       0x49u
#define KEY_HOME         0x4Au
#define KEY_PAGE_UP      0x4Bu
#define KEY_DELETE       0x4Cu
#define KEY_END          0x4Du
#define KEY_PAGE_DOWN    0x4Eu
#define KEY_RIGHT_ARROW  0x4Fu
#define KEY_LEFT_ARROW   0x50u
#define KEY_DOWN_ARROW   0x51u
#define KEY_UP_ARROW     0x52u

/* ファンクションキー: F13～F24 */
#define KEY_F13 0x68u
#define KEY_F14 0x69u
#define KEY_F15 0x6Au
#define KEY_F16 0x6Bu
#define KEY_F17 0x6Cu
#define KEY_F18 0x6Du
#define KEY_F19 0x6Eu
#define KEY_F20 0x6Fu
#define KEY_F21 0x70u
#define KEY_F22 0x71u
#define KEY_F23 0x72u
#define KEY_F24 0x73u

/*
 * 1つのキーを押す8バイトのBoot Keyboardレポートを作ります。
 * PRESS_KEYの次には必ずRELEASE_KEYSを置き、キーを離してください。
 */
#define PRESS_KEY(modifier, key) \
    {(modifier), 0u, (key), 0u, 0u, 0u, 0u, 0u}
#define RELEASE_KEYS \
    {MOD_NONE, 0u, KEY_NONE, 0u, 0u, 0u, 0u, 0u}

/* -------------------------------------------------------------------------
 * USBキーボード内部設定（通常は変更しません）
 * ------------------------------------------------------------------------- */

/* Boot Keyboardの入力レポートは、修飾キー1＋予約1＋通常キー6の8バイトです。 */
#define KEYBOARD_REPORT_SIZE 8u

/* キーボード入力レポートを返すUSB Endpoint番号です。 */
#define KEYBOARD_ENDPOINT 1

/* USB HIDの制御要求です。USB内部処理用なので通常は変更しません。 */
/* bmRequestTypeは下位バイト、bRequestは上位バイトへ格納されます。 */
#define HID_REQ_GET_REPORT   0x01A1u
#define HID_REQ_GET_IDLE     0x02A1u
#define HID_REQ_GET_PROTOCOL 0x03A1u
#define HID_REQ_SET_IDLE     0x0A21u
#define HID_REQ_SET_PROTOCOL 0x0B21u

/* スイッチ押下後、キー列の送信中なら1になります。USB処理からも参照します。 */
static volatile uint8_t sequence_active;

/* 次に送るkey_sequenceの要素番号です。USB処理からも参照します。 */
static volatile uint8_t sequence_index;

/* PCへ最後に送った8バイトのキーボードレポートです。 */
static uint8_t current_report[KEYBOARD_REPORT_SIZE];

/* PCから設定されるHID Idle Rateを保持します。 */
static uint8_t idle_rate;

/* 1はHID Report Protocol、0はBoot Protocolを表します。 */
static uint8_t keyboard_protocol = 1u;

/*
 * -------------------------------------------------------------------------
 * ここを編集すると、スイッチを押したときのキー入力を変更できます。
 *
 * 例:
 *   PRESS_KEY(MOD_CTRL, KEY_C), RELEASE_KEYS,       Ctrl+C
 *   PRESS_KEY(MOD_COMMAND, KEY_C), RELEASE_KEYS,    Command+C
 *   PRESS_KEY(MOD_NONE, KEY_F12), RELEASE_KEYS,     F12
 *   PRESS_KEY(MOD_SHIFT, KEY_EQUAL), RELEASE_KEYS,  Shift+=
 *
 * 現在は、大文字A、小文字b、大文字C、小文字d、大文字Eの順です。
 * -------------------------------------------------------------------------
 */
static const uint8_t key_sequence[][KEYBOARD_REPORT_SIZE] = {
    PRESS_KEY(MOD_SHIFT, KEY_A), RELEASE_KEYS,
    PRESS_KEY(MOD_NONE, KEY_B),  RELEASE_KEYS,
    PRESS_KEY(MOD_SHIFT, KEY_C), RELEASE_KEYS,
    PRESS_KEY(MOD_NONE, KEY_D),  RELEASE_KEYS,
    PRESS_KEY(MOD_SHIFT, KEY_E), RELEASE_KEYS
};

/* 送信する8バイトのレポートをcurrent_reportへコピーします。 */
static void copy_report(const uint8_t *source)
{
    uint8_t i; /* レポート内の何バイト目をコピーしているか */
    for (i = 0; i < KEYBOARD_REPORT_SIZE; i++) {
        current_report[i] = source[i];
    }
}

void usb_handle_user_in_request(struct usb_endpoint *e, uint8_t *scratchpad,
                                int endp, uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    (void)e;
    (void)scratchpad;
    (void)ist;

    if (endp == KEYBOARD_ENDPOINT) {
        if (sequence_active) {
            uint8_t index = sequence_index; /* 今回送るキー列の位置 */
            copy_report(key_sequence[index]);
            usb_send_data(current_report, KEYBOARD_REPORT_SIZE, 0, sendtok);
            index++;
            if (index >= (uint8_t)(sizeof(key_sequence) / sizeof(key_sequence[0]))) {
                sequence_index = 0;
                sequence_active = 0;
            } else {
                sequence_index = index;
            }
        } else {
            usb_send_data(current_report, KEYBOARD_REPORT_SIZE, 0, sendtok);
        }
    } else {
        usb_send_empty(sendtok);
    }
}

/* macOS requests these HID boot-keyboard states while attaching IOHIDFamily. */
void usb_handle_other_control_message(struct usb_endpoint *e,
                                      struct usb_urb *s,
                                      struct rv003usb_internal *ist)
{
    uint16_t request = s->wRequestTypeLSBRequestMSB; /* PCから届いたHID要求 */
    uint16_t value = (uint16_t)(s->lValueLSBIndexMSB & 0xffffu); /* 要求の設定値 */
    uint16_t length = s->wLength; /* PCが要求している応答バイト数 */
    (void)ist;

    switch (request) {
    case HID_REQ_GET_REPORT:
        e->opaque = current_report;
        e->max_len = (length < KEYBOARD_REPORT_SIZE) ? length : KEYBOARD_REPORT_SIZE;
        break;
    case HID_REQ_GET_IDLE:
        e->opaque = &idle_rate;
        e->max_len = (length < 1u) ? length : 1u;
        break;
    case HID_REQ_SET_IDLE:
        idle_rate = (uint8_t)(value >> 8);
        break;
    case HID_REQ_GET_PROTOCOL:
        e->opaque = &keyboard_protocol;
        e->max_len = (length < 1u) ? length : 1u;
        break;
    case HID_REQ_SET_PROTOCOL:
        keyboard_protocol = (uint8_t)(value & 0x01u);
        break;
    default:
        break;
    }
}

int main(void)
{
    SystemInit();
    funGpioInitAll();
    funPinMode(ENCODER_KEY_PIN, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(ENCODER_KEY_PIN, FUN_HIGH);

    Delay_Ms(1);
    usb_setup();

    uint8_t last_raw = (uint8_t)funDigitalRead(ENCODER_KEY_PIN); /* 直前の生入力 */
    uint8_t stable = last_raw; /* チャタリング除去後の確定状態 */
    uint8_t stable_count = 0; /* 同じ入力が続いたミリ秒数 */

    for (;;) {
        uint8_t raw = (uint8_t)funDigitalRead(ENCODER_KEY_PIN); /* 現在の生入力 */
        if (raw == last_raw) {
            if (stable_count < DEBOUNCE_MS) {
                stable_count++;
            }
        } else {
            last_raw = raw;
            stable_count = 0;
        }

        if (stable_count >= DEBOUNCE_MS && raw != stable) {
            stable = raw;
            if (stable == KEY_PRESSED_LEVEL && !sequence_active) {
                sequence_index = 0;
                sequence_active = 1;
            }
        }
        Delay_Ms(1);
    }
}
