<segmentation 예외처리>

- 특징값 100 기준으로 beep 시작값과 끝값을 찾기

- det1 
  - 앞의 ratio 값 5개 중에 100이상인 값의 개수
- det2 
  - 뒤의 ratio 값 5개 중에 100이상인 값의 개수

- beep 시작 값
  - det1 == 0 and det2 == 5 일때의 100이상의 ratio 값

- beep 끝 값 
  - beep음 구간이며, 100이하의 ratio 값이 나타나는 경우
  - a : det1 >= 3 인 경우(60%)는 beep음 도중의 예외값으로 인정
  - b : a가 아닌 경우, beep음 끝 값의 일부 중 하나로 인정(beep 끝 값) 
