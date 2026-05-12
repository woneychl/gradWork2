package com.example.choi; // 파일이 있는 폴더 경로와 맞춰주세요.

import com.example.choi.entity.User; // User 엔티티의 경로
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface UserRepository extends JpaRepository<User, UUID> {

    // 이메일로 유저 정보를 찾는 메서드
    // 스프링 데이터 JPA가 이 이름을 보고 자동으로 SQL 쿼리를 만들어줍니다.
    Optional<User> findByEmail(String email);
}
