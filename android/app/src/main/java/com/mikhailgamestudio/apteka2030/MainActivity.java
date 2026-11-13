package com.mikhailgamestudio.apteka2030;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.media.AudioManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.DisplayCutout;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.ConsoleMessage;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.window.OnBackInvokedDispatcher;

/**
 * Nizhnevartovsk 2030: Pharmacy — a full-screen shell around the self-contained game page
 * (assets/index.html). Offline, no permissions.
 */
public class MainActivity extends Activity {
    private static final String TAG = "Apteka2030";
    private static final String GAME_URL = "file:///android_asset/index.html";

    private FrameLayout root;
    private WebView web;
    private AlertDialog dialog;
    private final Handler ui = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        Window w = getWindow();
        w.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setVolumeControlStream(AudioManager.STREAM_MUSIC);
        if (Build.VERSION.SDK_INT >= 28) {
            WindowManager.LayoutParams lp = w.getAttributes();
            lp.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            w.setAttributes(lp);
        }

        root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        setContentView(root);

        // keep the game clear of the camera cut-out: the strip under it stays black
        if (Build.VERSION.SDK_INT >= 28) {
            root.setOnApplyWindowInsetsListener((v, insets) -> {
                DisplayCutout c = insets.getDisplayCutout();
                if (c != null) v.setPadding(c.getSafeInsetLeft(), c.getSafeInsetTop(), c.getSafeInsetRight(), c.getSafeInsetBottom());
                else v.setPadding(0, 0, 0, 0);
                return insets;
            });
        }

        if (Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                    OnBackInvokedDispatcher.PRIORITY_DEFAULT, this::confirmExit);
        }

        createWebView();
        hideSystemBars();
    }

    private void createWebView() {
        try {
            web = new WebView(this);
        } catch (Throwable e) {          // WebView package missing, disabled or being updated
            Log.e(TAG, "WebView is not available", e);
            web = null;
            showWebViewProblem();
            return;
        }
        web.setBackgroundColor(0xFF0E151A);
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.setVerticalScrollBarEnabled(false);
        web.setHorizontalScrollBarEnabled(false);
        web.setHapticFeedbackEnabled(false);
        web.setLongClickable(false);
        web.setOnLongClickListener(v -> true);      // no text-selection popups over the game

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);               // saves live in localStorage
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(true);
        s.setTextZoom(100);                         // the system font size must not break the layout
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setAllowFileAccess(false);                // android_asset is still readable
        s.setAllowContentAccess(false);
        s.setGeolocationEnabled(false);
        s.setCacheMode(WebSettings.LOAD_NO_CACHE);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        if (Build.VERSION.SDK_INT >= 26) s.setSafeBrowsingEnabled(false);

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage m) {
                if (m.messageLevel() == ConsoleMessage.MessageLevel.ERROR)
                    Log.e(TAG, "JS: " + m.message() + " @" + m.lineNumber());
                return true;
            }
        });
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                return u == null || !GAME_URL.equals(u.toString().split("[#?]")[0]);   // the game never leaves its page
            }

            @Override
            public void onPageFinished(WebView v, String url) {
                // has the game script really started? (it cannot on a very old WebView)
                ui.postDelayed(() -> {
                    if (web == null) return;
                    web.evaluateJavascript("(function(){return typeof window.__G})()", r -> {
                        boolean ok = r != null && r.contains("object");
                        Log.i(TAG, "game boot check: " + r);
                        if (!ok) showWebViewProblem();
                    });
                }, 2500);
            }

            @Override
            public boolean onRenderProcessGone(WebView v, RenderProcessGoneDetail d) {
                Log.e(TAG, "WebView renderer is gone, restarting the game");
                destroyWebView();
                ui.post(MainActivity.this::recreate);   // the autosave brings the player back
                return true;
            }
        });

        root.addView(web, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        web.loadUrl(GAME_URL);
    }

    private void destroyWebView() {
        if (web == null) return;
        try {
            root.removeView(web);
            web.stopLoading();
            web.destroy();
        } catch (Throwable ignored) {
        }
        web = null;
    }

    /* ---------- full screen ---------- */
    private void hideSystemBars() {
        Window w = getWindow();
        View decor = w.getDecorView();
        if (Build.VERSION.SDK_INT >= 30) {
            w.setDecorFitsSystemWindows(false);
            WindowInsetsController c = w.getInsetsController();
            if (c != null) {
                c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                c.hide(WindowInsets.Type.systemBars());
            }
        } else {
            decor.setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    | View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideSystemBars();
    }

    /* ---------- sound follows the app: silent in the background ---------- */
    private void js(String code) {
        if (web != null) web.evaluateJavascript("(function(){try{" + code + "}catch(e){}})()", null);
    }

    @Override
    protected void onPause() {
        js("var g=window.__G;if(g){if(g.A&&g.A.ctx)g.A.ctx.suspend();var a=g.NAR&&g.NAR.au;if(a&&!a.paused){a.pause();window.__nvHeld=1}}");
        if (web != null) web.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
        js("var g=window.__G;if(g){if(g.A&&g.A.ctx)g.A.ctx.resume();if(window.__nvHeld){window.__nvHeld=0;g.NAR.au.play()}}");
        hideSystemBars();
    }

    @Override
    protected void onDestroy() {
        if (dialog != null) dialog.dismiss();
        ui.removeCallbacksAndMessages(null);
        destroyWebView();
        super.onDestroy();
    }

    /* ---------- back button ---------- */
    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        confirmExit();
    }

    private void confirmExit() {
        if (isFinishing() || (dialog != null && dialog.isShowing())) return;
        dialog = new AlertDialog.Builder(this, android.R.style.Theme_Material_Dialog_Alert)
                .setTitle(R.string.exit_q)
                .setMessage(R.string.exit_hint)
                .setPositiveButton(R.string.yes, (d, i) -> finish())
                .setNegativeButton(R.string.no, null)
                .setOnDismissListener(d -> hideSystemBars())
                .create();
        dialog.show();
    }

    private void showWebViewProblem() {
        if (isFinishing() || (dialog != null && dialog.isShowing())) return;
        dialog = new AlertDialog.Builder(this, android.R.style.Theme_Material_Dialog_Alert)
                .setTitle(R.string.wv_title)
                .setMessage(R.string.wv_text)
                .setCancelable(false)
                .setPositiveButton(R.string.wv_open, (d, i) -> {
                    try {
                        startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=com.google.android.webview")));
                    } catch (Throwable e) {
                        try {
                            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/apps/details?id=com.google.android.webview")));
                        } catch (Throwable ignored) {
                        }
                    }
                    finish();
                })
                .setNegativeButton(R.string.wv_close, (d, i) -> finish())
                .create();
        dialog.show();
    }
}
