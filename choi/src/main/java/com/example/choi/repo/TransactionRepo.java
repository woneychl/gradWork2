package com.example.choi.repo; // 파일이 위치한 폴더 경로

import com.example.choi.entity.Transaction; // Transaction 엔티티 경로
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;


@Repository
public interface TransactionRepo extends JpaRepository<Transaction, UUID> {
    // 특정 계좌에서 발생한 모든 거래 내역 조회
    List<Transaction> findByFromAccountOrToAccount(String fromAccount, String toAccount);
}