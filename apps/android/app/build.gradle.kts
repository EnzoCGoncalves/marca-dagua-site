plugins { id("com.android.application") }

android {
    namespace = "com.enzocgoncalves.marcaflow"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.enzocgoncalves.marcaflow"
        minSdk = 23
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release { isMinifyEnabled = false }
    }
}

dependencies {
    implementation("com.google.androidbrowserhelper:androidbrowserhelper:2.5.0")
}
