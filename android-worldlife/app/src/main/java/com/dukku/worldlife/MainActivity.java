package com.dukku.worldlife;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.graphics.Color;
import android.view.Window;
import android.view.WindowManager;

public class MainActivity extends Activity {
  private WebView web;
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    Window w=getWindow();
    w.setStatusBarColor(Color.WHITE);
    w.setNavigationBarColor(Color.rgb(238,247,239));
    w.getDecorView().setSystemUiVisibility(android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
    web=new WebView(this);
    web.setBackgroundColor(Color.rgb(238,247,239));
    web.setWebViewClient(new WebViewClient());
    WebSettings s=web.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setAllowFileAccess(true);
    s.setAllowContentAccess(true);
    s.setMediaPlaybackRequiresUserGesture(false);
    web.loadUrl("file:///android_asset/index.html");
    setContentView(web);
  }
  @Override public void onBackPressed(){ if(web.canGoBack()) web.goBack(); else super.onBackPressed(); }
}