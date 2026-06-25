🎉 **DocTranslator Pro Version Now Released!** Welcome to experience more powerful features!

## ✨ Pro Version Core Advantages

- **Intelligent Chunking Strategy**: Better recognition of paragraphs, lists, and other structures to improve translation quality and contextual coherence.
- **Cost Optimization**: Significantly reduced token consumption through more efficient prompt design and injection strategies, effectively lowering translation costs.
- **Terminology Database**: Support for user-defined terminology comparison tables, ensuring accuracy and consistency of professional term translations.
- **Translation Memory**: Intelligently reuse historical translations to improve efficiency and reduce costs.
- **AI Model Provider Management**: Configure multiple large models such as OpenAI, Qwen, DeepSeek - users can choose according to their needs or use intelligent routing.
- **Batch Processing**: Support document uploads with multiple terminology databases and translation memories for concurrent translation with higher efficiency and accuracy.
- **Usage Statistics**: Provides token consumption statistics and other management backend functions.

[![Pro Version Online Experience](https://img.shields.io/badge/Pro%20Version-Online%20Experience-71a7f4?style=for-the-badge&logoColor=white)](https://pro.doctranslator.cn)  

---

# 📄 DocTranslator - AI Document Translation Tool 🚀

**DocTranslator** document translation supports multiple file format translations, is compatible with OpenAI format APIs, and supports batch operations and multi-threaded processing. Whether you're an individual user or enterprise team, DocTranslator can help you efficiently complete document translation tasks! ✨

[[English]](README_en.md)

---


| 🌐 **Online Experience**     | [Visit Now](https://dc.starpms.cn/) |
|:-----------------------------:|:------------------------------------:|
| 📚 **Official Documentation** | [View Docs](https://www.doctranslator.cn/)      |
| 👉 **Recommended API Gateway**| [Use Now](https://www.ezworkapi.com)     |




[🔥Recommended GPT Gateway - Low Price Discounts - Click Here🔥](https://www.ezworkapi.com) 

---

## 🌟 Features

- **Support Multiple Document Formats**  
  📑 **txt**, 📝 **markdown**, 📄 **word**, 📊 **csv**, 📈 **excel**, 📑 **pdf (non-scanned)**, 📽️ **ppt** document AI translation.
  

- **Compatible with OpenAI Format APIs**  
  🤖 Supports any endpoint API that complies with OpenAI format (gateway APIs), flexibly adapting to various AI models.

- **Batch Operations**  
  🚀 Supports batch uploading and translating documents to improve work efficiency.

- **Multi-threading Support**  
  ⚡ Utilizes multi-threading technology to accelerate document translation processes.

- **Docker Deployment**  
  🐳 Supports one-click Docker deployment, simple and easy to use.

---

## 🛠️ Tech Stack

- **Frontend**: Vue 3 + Vite  
- **Backend**: Python + Flask + MySQL/SQLite  
- **AI Translation**: Compatible with OpenAI format 
- **Deployment**: Docker + Nginx  

---

## Demo Screenshots:
### User Interface Demo
![User Interface](docs/images/image1.png)
![User Interface 2](docs/images/image2.png)
![User Interface 3](docs/images/image.png)

### Admin Interface Demo
![Admin Interface](docs/images/image3.png)
![Admin Interface 2](docs/images/image4.png)
![Admin Interface 3](docs/images/image5.png)

## One-Click Deployment
```bash

git clone https://github.com/mingchen666/DocTranslator.git
cd DocTranslator

# 2. Configure backend environment variables (Important!)
cp backend/.env.example backend/.env
# Then edit backend/.env file and fill in database information

# 3. One-click deployment
chmod +x deploy.sh && ./deploy.sh

```


## 🚀 Local Development

### 1. Clone the Project

```bash
git clone https://github.com/mingchen666/DocTranslator.git
cd DocTranslator
```

### 2. Configure Environment Variables

Fill in necessary environment variables in the `backend/.env` file


### 3. Start Backend

Enter backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 4. Start Backend

```bash
python app.py
```

### 5. Start Frontend and Admin
> **The /dist folder is already built and can be deployed directly. Skip the following steps if not developing locally**
>

*Frontend*

```bash
cd frontend
pnpm install
pnpm dev
```

*Admin*

```bash
cd admin
pnpm install
pnpm dev
```


### 6. Access the Project

- **Frontend**: http://localhost:1475  
- **Admin**: http://localhost:8081  
- **Backend API**: http://localhost:5000  

---


## 🐳 Option 1: Docker Deployment (Online Image Beta Version)

### 1. Create Docker Network

```bash
docker network create my-network
```

### 2. Run Backend Container

```bash
cd ..
docker run -d \
  --name backend-container \
  --network my-network \
  -p 5000:5000 \
  -v $(pwd)/backend/db:/app/db \
  eggsunsky/doctranslator:latest
```
### 3. Start Nginx

```bash
docker run -d \
  --name nginx-container \
  -p 1475:80 \
  -p 8081:8081 \
  -v $(pwd)/nginx/nginx.conf:/etc/nginx/conf.d/default.conf \
  -v $(pwd)/frontend/dist:/usr/share/nginx/html/frontend \
  -v $(pwd)/admin/dist:/usr/share/nginx/html/admin \
  --network my-network \
  nginx:stable-alpine
```

### 4. Access Services

- **Frontend**: http://localhost:1475  
- **Admin**: http://localhost:8081  
- **Backend API**: http://localhost:5000 

## 🐳 Option 2: Docker Deployment (Build Your Own Image)

### 1. Project Structure

```plaintext
DocTranslator/
├── frontend/          # Frontend code
├── admin/             # Admin code
├── backend/           # Backend code
├── nginx/             # Nginx configuration
│   └── nginx.conf     # Nginx configuration file
```

### 2. Create Docker Network

```bash
docker network create my-network
```

### 3. Backend Deployment

#### 3.1 Configure Environment Variables

Ensure the `DocTranslator/backend/.env` file has been filled in correctly with environment variables.

#### 3.2 Build Backend Image

```bash
cd DocTranslator/backend
docker build -t doctranslator .
```

#### 3.3 Run Backend Container

```bash
cd ..
docker run -d \
  --name backend-container \
  --network my-network \
  -p 5000:5000 \
  -v $(pwd)/backend/db:/app/db \
  doctranslator
```

### 4. Start Nginx

```bash
docker run -d \
  --name nginx-container \
  -p 1475:80 \
  -p 8081:8081 \
  -v $(pwd)/nginx/nginx.conf:/etc/nginx/conf.d/default.conf \
  -v $(pwd)/frontend/dist:/usr/share/nginx/html/frontend \
  -v $(pwd)/admin/dist:/usr/share/nginx/html/admin \
  --network my-network \
  nginx:stable-alpine
```

### 5. Access Services

- **Frontend**: http://localhost:1475  
- **Admin**: http://localhost:8081  
- **Backend API**: http://localhost:5000  
  - *Account*: admin ; *Password*: 123456

---

## 🐳 Option 3: Docker-Compose Deployment (Build Your Own Image)
###  Start Project
```shell
cd DocTranslator
docker-compose up -d
```

### Update Project
```shell
cd /DocTranslator
docker compose down
git pull
docker compose pull
docker compose up -d
```


## 💖 Support & Appreciation

Maintaining this project requires considerable effort. If DocTranslator has helped you, feel free to support us! Your support is my motivation to continue development! 😊  
<img src="docs/e652698b250efb6e5151b084bd08814.jpg" alt="Support QR Code" width="300">
---

## 📢 Community Group
For any questions or discussions, welcome to join our community group
<img src="docs/images/qq-group.png" alt="Community Group" width="300">


## 🤝 Contribution Guide

Contributions are welcome!

---

## 📜 License

[Apache-2.0 license](LICENSE)

---



## 📞 Contact Me

For any questions or suggestions, please contact me:  
---

## 👋 About Me

A student who likes frontend development and enjoys exploring AI applications and tool development
🎉 Thanks for everyone's support! Welcome to Star ⭐️ and Fork 🍴, let's improve DocTranslator together!


## 📌 Note

This project is based on [ezwork](https://github.com/EHEWON/ezwork-ai-doc-translation) with refactoring and optimization, thanks to the original author's contribution! 🙏

## 🙏 Acknowledgments

  [BabelDOC](https://github.com/funstory-ai/BabelDOC)

[![Star History](https://api.star-history.com/svg?repos=mingchen666/DocTranslator&type=Date)](https://star-history.com/#mingchen666/DocTranslator)
