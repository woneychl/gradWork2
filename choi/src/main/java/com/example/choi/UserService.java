package com.example.choi; // 패키지 경로는 본인의 폴더 위치에 맞추세요!

import com.example.choi.entity.User;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserService {

    @Autowired
    private UserRepository userRepository; // 1. DB와 통신하는 진짜 창구
    private final BCryptPasswordEncoder passwordEncoder;

    public User registerUser(String email, String password, String name) {
        User newUser = new User();
        newUser.setEmail(email);
        String encodedPassword = passwordEncoder.encode(password); //비번 해시화
        newUser.setPassword(encodedPassword);
        newUser.setUsername(name);

        return userRepository.save(newUser); // DB에 쏙! 저장됩니다.
    }

    // 2. 로그인 확인: 이메일과 비번이 DB와 일치하는지 체크
    public boolean checkLogin(String email, String password) {
        return userRepository.findByEmail(email)
                .map(user -> {
                    return passwordEncoder.matches(password, user.getPassword());
                })
                .orElse(false);
    }
    public User getUserByEmail(String email) {
        // 2. userRepository에게 이메일로 유저를 찾아오라고 시킵니다.
        // 만약 유저가 없다면 에러(RuntimeException)를 던지도록 안전장치를 합니다.
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("유저를 찾을 수 없습니다: " + email));
    }
}