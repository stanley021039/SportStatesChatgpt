// Immediately Invoked Function Expression (IIFE)
(function () {
  var userNameElement = document.querySelector('.user-name');
  if (userNameElement) {
    const token = localStorage.getItem('token');
    fetch('/SportStatesChatgpt/ID_verify', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'qwdadrization': `Bearer ${token}`,
      },
      credentials: 'same-origin',  // 允许发送Cookie
    })
      .then(response => response.json())
      .then(data => {
        data.current_user ? userNameElement.textContent = data.current_user : userNameElement.textContent = '請登入';
        console.log(data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }
})();

function searchTeam() {
    const userInput = document.getElementById('userInput').value;

    fetch("/SportStatesChatgpt/get_score", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // 在页面上显示后端返回的 JSON 数据
        document.getElementById("wins").textContent = "勝場：" + data.wins;
        document.getElementById("losses").textContent = "敗場：" + data.losses;
    })
    .catch(error => {
        console.error('Fetch Error:', error);
    });
}

function chat_with_gpt() {
    var userInput = document.getElementById("textInput").value;

    // 修改文本的样式
    fetch("/SportStatesChatgpt/chat", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // 在页面上显示后端返回的 JSON 数据
        document.getElementById("response").textContent = data.response;
    })
    .catch(error => {
        console.error('Fetch Error:', error);
    });
}

// 创建用户
if (document.getElementById("createUserForm")) {
  document.getElementById("createUserForm").addEventListener("submit", function (event) {
      event.preventDefault();
      const newUsername = document.getElementById("newUsername").value;
      const newPassword = document.getElementById("newPassword").value;
      const newsex = document.getElementById("sex").value;
      createUser(newUsername, newPassword, newsex);
  });
}

// 登入
if (document.getElementById("login")) {
  console.log('login')
  document.getElementById("login").addEventListener("submit", function (event) {
    event.preventDefault();
    const username = document.getElementById("Username").value;
    const password = document.getElementById("Password").value;
    login(username, password);
  });
}

// 修改密碼
if (document.getElementById("changepw")) {
  document.getElementById("changepw").addEventListener("submit", function (event) {
    event.preventDefault();
    const Username_change = document.getElementById("Username_change").value;
    const Password_change = document.getElementById("Password_change").value;
    updateUser(Username_change, Password_change);
  });
}

// 刪除帳號
if (document.getElementById("deleteuser")) {
  document.getElementById("deleteuser").addEventListener("submit", function (event) {
    event.preventDefault();
    const Username_del = document.getElementById("Username_del").value;
    const Password_del = document.getElementById("Password_del").value;
    deleteUser(Username_del, Password_del);
  });
}

// 用戶資訊
if (document.getElementById("userinfo")) {
  document.getElementById("userinfo").addEventListener("submit", function (event) {
    event.preventDefault();
    const Username = document.getElementById("Username").value;
    const token = localStorage.getItem('token');
    infoUser(Username, token);
  });
}

function createUser(username, password, sex) {
    const apiUrl = `/SportStatesChatgpt/user/${username}`; // 根据您的后端端点设置正确的 URL
    const userData = {
      username: username,
      password: password,
      sex: sex
    };

    fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    })
      .then(response => response.json())
      .then(data => {
        document.getElementById("response_createUser").textContent = data.message;
        console.log(data.message); // 输出服务器返回的消息
      })
      .catch(error => {
        console.error('创建用户时出错:', error);
      });
  }

  // 更新用户密码
  function updateUser(username, newPassword) {
    console.log(username);
    const apiUrl = `/SportStatesChatgpt/user/${username}`; // 根据您的后端端点设置正确的 URL
    const userData = {
      username: username,
      password: newPassword
    };

    fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    })
      .then(response => response.json())
      .then(data => {
        document.getElementById("response_changepw").textContent = data.message;
        console.log(data.message); // 输出服务器返回的消息
      })
      .catch(error => {
        console.error('更新用户密码时出错:', error);
      });
  }

  // 删除用户
  function deleteUser(username, password) {
    const apiUrl = `/SportStatesChatgpt/user/${username}`; // 根据您的后端端点设置正确的 URL
    const userData = {
      username: username,
      password: password
    };
    fetch(apiUrl, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    })
      .then(response => response.json())
      .then(data => {
        document.getElementById("response_deluser").textContent = data.message;
        console.log(data.message); // 输出服务器返回的消息
      })
      .catch(error => {
        console.error('删除用户时出错:', error);
      });
  }

function login(username, password) {
  const apiUrl = '/SportStatesChatgpt/user/login'; // 根据您的后端端点设置正确的 URL
  const userData = {
    username: username,
    password: password
  };

  fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.token) {
      localStorage.setItem('token', data.token);
      console.log(data.message)
      document.getElementById("response_login").textContent = data.message;
    } else {
      // 登录失败，显示错误消息
      console.log(data.message)
      document.getElementById("response_login").textContent = '登录失败: ' + data.message;
    }
  })
  .catch(error => {
    console.error('登入時出错:', error);
  });
}

function infoUser(username, token) {
  console.log(token)
  const apiUrl = `/SportStatesChatgpt/user/${username}`; // 根据您的后端端点设置正确的 URL
  token_str = String(token)
  fetch(apiUrl, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'qwdadrization': `Bearer ${token}`,
      'X-User-Data': username, // 将用户数据转为 JSON 字符串
    },
  })
  .then(response => response.json())
  .then(data => {
    if (data.message=="user found") {
      document.getElementById("response_username").textContent = "使用者名稱：" + data.username;
      document.getElementById("response_coin").textContent = "代幣：" + data.coin;
      document.getElementById("response_sex").textContent = "性別：" + data.sex;
    }
    else {
      document.getElementById("response_username").textContent = "使用者名稱未找到";
      document.getElementById("response_coin").textContent = "代幣：";
      document.getElementById("response_sex").textContent = "性別：";
    }
    console.log(data.message); // 输出服务器返回的消息
  })
  .catch(error => {
    console.error('登录时出错:', error);
  });
}