const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');

// 認証に必要なスコープ
const SCOPES = ['https://www.googleapis.com/auth/calendar'];

// トークンファイルのパス
const TOKEN_FILE = 'token.json';
// クライアントシークレットファイルのパス
const CLIENT_SECRET_FILE = 'client_secret.json';

/**
 * GoogleカレンダーAPIの認証情報を取得する
 * @returns {Promise<google.auth.OAuth2>} 認証済みのOAuth2クライアント
 */
async function getCredentials() {
  // クライアントシークレットファイルを読み込む
  const content = fs.readFileSync(CLIENT_SECRET_FILE);
  const credentials = JSON.parse(content);
  const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;
  
  // OAuth2クライアントを作成
  const oAuth2Client = new google.auth.OAuth2(
    client_id, client_secret, redirect_uris[0]
  );

  let creds = null;
  
  // トークンファイルが存在する場合は読み込む
  if (fs.existsSync(TOKEN_FILE)) {
    const token = JSON.parse(fs.readFileSync(TOKEN_FILE));
    oAuth2Client.setCredentials(token);
    creds = token;
  }
  
  // 認証情報が無効または存在しない場合は新たに取得
  if (!creds || isTokenExpired(creds)) {
    if (creds && creds.refresh_token) {
      try {
        console.log("トークンの有効期限が切れています。リフレッシュトークンを使用して自動的に更新します...");
        await refreshAccessToken(oAuth2Client);
        console.log("トークンが正常に更新されました。");
      } catch (e) {
        console.error(`トークンの更新に失敗しました: ${e}`);
        console.log("新しい認証フローを開始します...");
        await getNewToken(oAuth2Client);
      }
    } else {
      console.log("新しい認証フローを開始します...");
      await getNewToken(oAuth2Client);
    }
  }
  
  return oAuth2Client;
}

/**
 * トークンの有効期限が切れているかどうかを確認する
 * @param {Object} token トークン情報
 * @returns {boolean} トークンの有効期限が切れている場合はtrue
 */
function isTokenExpired(token) {
  if (!token.expiry_date) return true;
  return token.expiry_date <= Date.now();
}

/**
 * アクセストークンをリフレッシュする
 * @param {google.auth.OAuth2} oAuth2Client OAuth2クライアント
 * @returns {Promise<void>}
 */
async function refreshAccessToken(oAuth2Client) {
  return new Promise((resolve, reject) => {
    oAuth2Client.refreshAccessToken((err, token) => {
      if (err) {
        reject(err);
        return;
      }
      oAuth2Client.setCredentials(token);
      // トークンを保存
      fs.writeFileSync(TOKEN_FILE, JSON.stringify(token));
      console.log(`新しいトークンが ${TOKEN_FILE} に保存されました。`);
      resolve();
    });
  });
}

/**
 * 新しいトークンを取得する
 * @param {google.auth.OAuth2} oAuth2Client OAuth2クライアント
 * @returns {Promise<void>}
 */
async function getNewToken(oAuth2Client) {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent'
  });
  
  console.log(`\n\n認証URLにアクセスして認証を行ってください: ${authUrl}\n\n`);
  
  // ローカルサーバーを起動して認証コードを受け取る
  return new Promise((resolve, reject) => {
    const server = require('http').createServer(async (req, res) => {
      try {
        // URLからcodeパラメータを取得
        const url = new URL(req.url, 'http://localhost');
        const code = url.searchParams.get('code');
        
        if (code) {
          // サーバーをクローズ
          res.end('認証が完了しました。このページを閉じてください。');
          server.close();
          
          // トークンを取得
          const { tokens } = await oAuth2Client.getToken(code);
          oAuth2Client.setCredentials(tokens);
          
          // トークンを保存
          fs.writeFileSync(TOKEN_FILE, JSON.stringify(tokens));
          console.log(`新しいトークンが ${TOKEN_FILE} に保存されました。`);
          
          resolve();
        } else {
          res.end('認証コードが見つかりませんでした。もう一度お試しください。');
        }
      } catch (e) {
        reject(e);
      }
    }).listen(3000);
    
    console.log('ローカルサーバーを起動しました。ブラウザで認証を完了すると自動的に処理が続行されます。');
  });
}

// メイン処理
if (require.main === module) {
  console.log("GoogleカレンダーAPIの認証を開始します...");
  getCredentials()
    .then(() => {
      console.log(`認証が完了しました。トークンが ${TOKEN_FILE} に保存されました。`);
    })
    .catch(err => {
      console.error('認証中にエラーが発生しました:', err);
    });
}

module.exports = { getCredentials };
