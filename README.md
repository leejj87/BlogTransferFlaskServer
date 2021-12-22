# flaskServer_for_blog

*Parsing the Naver Blog Contents

*python 3.7

*run.py 로 작동

*테스트
  http://127.0.0.1:5000/naver?naverID={네이버아이디}&article={블로그_글번호}

*log 체크
  http://127.0.0.1:5000/logs
  http://127.0.0.1:5000/systemlogs

*요청
  get 타입 요청.
  http://127.0.0.1:5000/    --> 버전 및 기본소개
  http://127.0.0.1:5000/naver?naverID={네이버아이디}&article={블로그_글번호}  --> 기본요청
  http://127.0.0.1:5000/logs  -->로그정보
* return

  Json format
  {"details":[{contents block1},{contents block2},{contents block3}...],
  "source": sources (uft-8),
  "title": title (uft-8),
  "tags":[tag1,tag2,..]}
  
  추가 정보
  
 
  
  -details
    1. STRUCTURE
      array[json1,json2,json3]
    2. CONTENTS(타입별 구분)
      1) text
        - key:id, values: Div 클래스 id 값
        - key:contents , values: json {"all_contents": str  텍스트 Div 전체 string, "contents_separation": array[json{"style": str 각 문장별 스타일,"id":str 각문장별 span id,"span_text":str 각문장별 텍스트}]}
       2) horizontalline
        - key:id, values: Div 클래스 id 값
        - key:contents , values: json{"all_contents":'\n'}
        
       3) sticker
        - key:id, values: Div 클래스 id 값
        - key:contents , values: array[json{"data_linkdata": json 구조 스티거 링크데이터(스티거 상세정보), "img":json 구조 스티커 이미지 정보(이미지 링크 스타일 등)}]
        4) oembed
         - key:id, values: Div 클래스 id 값
         - key:contents , values: json{"embed_tag":embed iframe 태그 코드, "embed_details": json 형식 embed 코드 스크립 정보}
        5) image
         - key:id, values: Div 클래스 id 값
         - key:contents , values: json{"img":array[json{"style":이미지별 스타일,"href_data":json 형식 이미지 링크데이터, "img_lazyTag":json 형식 이미지 링크 정보}],"text":array[json{"style": str 텍스트 스타일,"text":str 텍스트 정보}]}
        6) oglink
         - key:id, values: Div 클래스 id 값
         - key:contents , values: json{"thumbnail":json{"thumb_href": json 형식 thumb 이미지 attrs,"thumb_img":str thumb 이미지 url},"link_detail":json{"title":str제목,"summary":str요약정보,"base_url": str 원본 url,"href":json 형식 링크정보 attrs}}
        7) video
         - key:id, values: Div 클래스 id 값
         - key:contents , values: json{"video_tags":json{"video_tag_info": json 형식 iframe 태그 attrs, "video_tag_source": str iframe 태그, "video_src":str 비디오 소스url},"script":json형식 비디오 데이터 모듈}
         8) quotation
         - key:id, values: Div 클래스 id 값
         - key:contents , values: json{"text":array[json{"p_style":str p태그 스타일,"s_style":str span 태그 스타일,"text": str 텍스트}]}
          9) map
          -key:id, values: Div 클래스 id 값
          -key:contents , values: json{"map_img_src":str 맵 이미지 소스, "map_data":json 형식 링크 상세정보, "map_src": str 맵 링크}
          10) mr_blog
           -key:id, values: Div 클래스 id 값
           -key:contents , values: json{"text":json{"all_texts":str 전체 텍스트},"strong":array[json{"text":str string 태그 텍스트}],"p":array[json{"text":str p 태그 텍스트}]}
          12) table
            -key:id, values: Div 클래스 id 값
            -key:contents , values: json{"style":str 테이블 스타일, "table":array[array[json{"style":str row 스타일,"contents":str 텍스트}]]}
*Install packages

  requirement.txt 로 패키지 설치 후 테스트.

*Structure

  -src
    -blogTransfer
      -__init__.py
      -flask_managing.py
      -selenium_management.py
      -tag_managerment.py
     -__init__.py
   -requirements.txt
   -run.py
   -worker.py
   -wsgi.py
   
 업데이트 정보
  실행: worker.py 실행 필수 --> 데몬 추가.
  ** 노드로 실행파일 만듬.
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
    export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    
    nvm install 16
    nvm use 16
    npm i -g pm2
    pm2 start worker.sh
    pm2 startup 명령어 한번 실행 후
    pm2 save
    

  설치됨: redis-server
  pip 설치됨: redis, rq
  
