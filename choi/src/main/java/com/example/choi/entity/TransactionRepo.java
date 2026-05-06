@Repository
public interface TransactionRepository extends JpaRepository<Transaction, UUID> {
    // 특정 계좌에서 발생한 모든 거래 내역 조회
    List<Transaction> findByFromAccountOrToAccount(String fromAccount, String toAccount);
}