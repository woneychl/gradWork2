package com.example.choi;

import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import lombok.RequiredArgsConstructor;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;

@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;
    private Map<String, String> codeStorage = new HashMap<>();

    @Async
    public void sendVerificationCode(String email) {
        String code = String.valueOf(new Random().nextInt(899999) + 100000); // 6자리 랜덤 번호
        codeStorage.put(email, code); // 메모장에 저장

        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(email);
        message.setSubject("[졸업작품] 이메일 인증 번호입니다.");
        message.setText("인증번호는 [" + code + "] 입니다.");

        mailSender.send(message);
    }

    // 2. 사용자가 입력한 번호가 메모장에 있는 거랑 맞는지 확인
    public boolean checkCode(String email, String code) {
        String savedCode = codeStorage.get(email);
        // 2. 로그를 찍어서 눈으로 직접 확인해봅니다 (서버 콘솔창 확인용)
        System.out.println("검증 요청 - 이메일: " + email);
        System.out.println("저장된 번호: [" + savedCode + "]");
        System.out.println("입력한 번호: [" + code + "]");

        // 3. 값이 비어있지 않은지, 그리고 앞뒤 공백을 제거(.trim())하고 비교합니다.
        if (savedCode == null || code == null) return false;
        return savedCode.trim().equals(code.trim());
        //return code != null && code.equals(savedCode);
    }
}