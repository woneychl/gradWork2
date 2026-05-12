package com.example.choi;

import lombok.RequiredArgsConstructor;
import com.example.choi.entity.User;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class UserController {

    private final EmailService emailService;
    private final UserService userService;
    private final JwtUtil jwtUtil;

    // 1. 이메일로 인증번호 보내기 요청
    @PostMapping("/send-code")
    public ResponseEntity<?> sendCode(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        System.out.println("인증 요청 온 이메일: " + email);
        emailService.sendVerificationCode(email);
        return ResponseEntity.ok(Map.of("message", "인증번호가 발송되었습니다."));
    }

    // 2. 사용자가 입력한 번호가 맞는지 확인
    @PostMapping("/verify-code")
    public ResponseEntity<Boolean> verifyCode(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String code = request.get("code");
        boolean isSuccess = emailService.checkCode(email, code);
        return ResponseEntity.ok(isSuccess);
    }

    @PostMapping("/signup")
    public ResponseEntity<?> signup(@RequestBody Map<String, String> userData) {
        try {
            // Flutter에서 보낸 데이터 꺼내기
            String email = userData.get("email");
            String password = userData.get("password");
            String name = userData.get("name");

            User savedUser = userService.registerUser(email, password, name);
            String token = jwtUtil.createToken(savedUser.getEmail());

            Map<String, String> response = new HashMap<>();
            response.put("token", token);
            response.put("email", savedUser.getEmail());
            response.put("status", "success");

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("fail");
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String password = request.get("password");

        // 1. DB에서 유저 확인 (아이디, 비번 체크)
        if (userService.checkLogin(email, password)) {
            String token = jwtUtil.createToken(email);

            Map<String, String> response = new HashMap<>();
            response.put("token", token);
            response.put("email", email);

            return ResponseEntity.ok(response);
        }
        return ResponseEntity.status(401).body("로그인 실패");
    }
}