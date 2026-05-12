package com.example.choi.repo;

import com.example.choi.entity.Card;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface CardRepo extends JpaRepository<Card, UUID> {
    // 특정 유저의 카드 목록을 가져오는 메서드
    List<Card> findByUser_UserId(UUID userId);
}