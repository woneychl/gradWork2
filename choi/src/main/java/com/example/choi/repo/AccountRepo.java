package com.example.choi.repo; // 현재 파일이 들어있는 폴더 경로

import com.example.choi.entity.Account; // Account 엔티티가 있는 경로
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface AccountRepo extends JpaRepository<Account, UUID> {
    // 특정 유저의 모든 계좌를 찾는 메서드
    List<Account> findByUser_UserId(UUID userId);

    // 계좌 번호로 특정 계좌를 찾는 메서드
    Optional<Account> findByAccountNumber(String accountNumber);
}